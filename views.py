import json
import os
import random
import traceback
from datetime import datetime
from io import BytesIO
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for, send_file
from flask_login import current_user, login_required
from sqlalchemy import func
from werkzeug.security import check_password_hash

from models import (db, User, Experiment, NlpAnalysis, TimelineSegment, Keyword, TrackingAnalysis, ChartBin, DetectedQuestion)
from minio_config import get_minio_client, BUCKETS, ensure_buckets

views = Blueprint("views", __name__)

# Configuration
RAW_CROPS_BUCKET = BUCKETS['RAW_CROPS']
LABELED_BUCKET = BUCKETS['LABELED_DATA']
JOBS_BUCKET = BUCKETS['LABELING_JOBS']

# Minio Helper Functions

def ensure_annotation_buckets():
    """Ensure annotation buckets exist."""
    ensure_buckets([RAW_CROPS_BUCKET, LABELED_BUCKET, JOBS_BUCKET])

def get_job_status(job_id):
    """Retrieve job status JSON from MinIO."""
    try:
        client = get_minio_client()
        response = client.get_object(JOBS_BUCKET, f"{job_id}/status.json")
        return json.loads(response.read().decode())
    except Exception:
        return None

def save_job_status(job_id, status_data):
    """Save updated job status to MinIO."""
    client = get_minio_client()
    data = json.dumps(status_data).encode()
    client.put_object(
        JOBS_BUCKET,
        f"{job_id}/status.json",
        BytesIO(data),
        len(data),
        content_type="application/json"
    )

def get_all_annotation_jobs():
    """List and sort all annotation jobs."""
    client = get_minio_client()
    jobs = []
    try:
        objects = client.list_objects(JOBS_BUCKET, recursive=False)
        for obj in objects:
            job_id = obj.object_name.rstrip('/')
            status = get_job_status(job_id)
            if status:
                jobs.append(status)
    except Exception:
        pass
    return sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)

def copy_images_to_labeled(job_id, group_id, person_id, max_images=250):
    """Moves images from raw crops to the labeled bucket structure."""
    client = get_minio_client()
    prefix = f"{job_id}/{group_id}/"
    copied = []
    
    status = get_job_status(job_id)
    experiment_name = status.get('experiment_name', job_id) if status else job_id
    
    try:
        all_objects = list(client.list_objects(RAW_CROPS_BUCKET, prefix=prefix, recursive=True))
        image_objects = [obj for obj in all_objects if obj.object_name.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Sample if too many images exist
        if len(image_objects) > max_images:
            image_objects = random.sample(image_objects, max_images)
        
        for obj in image_objects:
            response = client.get_object(RAW_CROPS_BUCKET, obj.object_name)
            data = response.read()
            filename = obj.object_name.split('/')[-1]
            
            dest_path = f"{experiment_name}/{person_id}/{group_id}_{filename}"
            
            client.put_object(
                LABELED_BUCKET,
                dest_path,
                BytesIO(data),
                len(data),
                content_type="image/jpeg"
            )
            copied.append(dest_path)
    except Exception as e:
        print(f"Error copying images: {e}")
    return copied

def update_session_metadata(experiment_name, new_data):
    """Update metadata.json for a session with additional fields."""
    client = get_minio_client()
    metadata_path = f"{experiment_name}/metadata.json"
    
    try:
        response = client.get_object('tastelab-videos-sorted', metadata_path)
        metadata = json.loads(response.read().decode())
        
        metadata.update(new_data)
        
        data = json.dumps(metadata, indent=2).encode()
        client.put_object(
            'tastelab-videos-sorted',
            metadata_path,
            BytesIO(data),
            len(data),
            content_type="application/json"
        )
        return True
    except Exception as e:
        print(f"Error updating metadata for {experiment_name}: {e}")
        return False


# Page routes
@views.route("/")
@login_required
def home():
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    selected_exp_id = request.args.get('exp_id', type=int)
    
    selected_experiment = Experiment.query.get(selected_exp_id) if selected_exp_id else (all_experiments[0] if all_experiments else None)
    
    nlp_analysis = selected_experiment.nlp_analysis if selected_experiment else None
    tracking_analysis = selected_experiment.tracking_analysis if selected_experiment else None

    # Aggregates
    avg_duration_sec = db.session.query(func.avg(Experiment.duration_seconds)).scalar() or 0
    total_duration_sec = db.session.query(func.sum(Experiment.duration_seconds)).scalar() or 0
    
    stats = {
        'total_experiments': Experiment.query.count(),
        'total_participants': db.session.query(func.sum(Experiment.participant_count)).scalar() or 0,
        'avg_participants': round(db.session.query(func.avg(Experiment.participant_count)).scalar() or 0, 1),
        'avg_duration': int(avg_duration_sec / 60), 
        'completed_experiments': Experiment.query.count(),
        'this_month': Experiment.query.filter(Experiment.date >= datetime.now().replace(day=1, hour=0, minute=0, second=0)).count()
    }
    
    # Recent & Trending
    recent_activity = Experiment.query.order_by(Experiment.date.desc()).limit(5).all()
    trend_data = Experiment.query.order_by(Experiment.date.asc()).all()
    
    participant_trend = {
        'labels': [exp.title[:15] + '...' if len(exp.title) > 15 else exp.title for exp in trend_data],
        'data': [exp.participant_count or 0 for exp in trend_data]
    }
    
    # Tag Processing
    tags_query = db.session.query(Experiment.tags).filter(Experiment.tags.isnot(None)).all()
    tag_counts = {}
    for (tags_str,) in tags_query:
        if tags_str:
            for tag in tags_str.split(','):
                tag_counts[tag.strip()] = tag_counts.get(tag.strip(), 0) + 1
    
    insights = {
        'avg_duration': int(avg_duration_sec / 60),
        'total_duration': int(total_duration_sec / 60),
        'this_month': stats['this_month'],
        'last_experiment': all_experiments[0] if all_experiments else None
    }
    
    top_experiments = Experiment.query.order_by(Experiment.participant_count.desc()).limit(5).all()
    
    return render_template("home.html", 
                           user=current_user,
                           experiments=all_experiments,
                           selected_experiment=selected_experiment,
                           nlp_analysis=nlp_analysis,
                           tracking_analysis=tracking_analysis,
                           stats=stats,
                           recent_activity=recent_activity,
                           tag_counts=tag_counts,
                           participant_trend=participant_trend,
                           insights=insights,
                           top_experiments=top_experiments)

@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_password = request.form.get("password")
        if not check_password_hash(current_user.password, current_password):
            flash("Incorrect password. Changes not saved.", category="error")
            return redirect(url_for("views.profile"))

        user = User.query.get(current_user.id)
        user.email = request.form.get("email")
        user.first_name = request.form.get("firstName")
        user.last_name = request.form.get("lastName")

        db.session.commit()
        flash("Changes saved successfully!", category="success")
        return redirect(url_for("views.profile"))

    return render_template("profile.html", user=current_user)

@views.route("/help")
@login_required
def help():
    return render_template("help.html", user=current_user)

@views.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html", user=current_user)

@views.route("/terms-of-service")
def terms_of_service():
    return render_template("terms-of-service.html", user=current_user)

@views.route("/experiments")
@login_required
def experiments():
    recent_experiments = Experiment.query.order_by(Experiment.date.desc()).limit(6).all()
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    archived_experiments = Experiment.query.filter_by(status="Archived").order_by(Experiment.date.desc()).all()
    
    # Filter Tags
    tags_query = db.session.query(Experiment.tags).filter(Experiment.tags.isnot(None)).all()
    all_tags = set()
    for (tags_str,) in tags_query:
        if tags_str:
            all_tags.update([t.strip() for t in tags_str.split(',') if t.strip()])
    
    # Filter Periods
    date_periods = set()
    for exp in all_experiments:
        if exp.date:
            date_periods.add(exp.date.strftime('%B %Y'))
    
    sorted_periods = sorted(
        list(date_periods),
        key=lambda x: datetime.strptime(x, '%B %Y'),
        reverse=True
    )
            
    return render_template("experiments.html",
                           user=current_user,
                           recent_experiments=recent_experiments,
                           all_experiments=all_experiments,
                           archived_experiments=archived_experiments,
                           tags=sorted(list(all_tags)),
                           date_periods=sorted_periods)

@views.route('/experiments/add-experiment', methods=['GET', 'POST'])
@login_required
def add_experiment():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if Experiment.query.filter(Experiment.title.ilike(title)).first():
            flash("An experiment with this title already exists.", category="error")
            return redirect(url_for('views.add_experiment'))
        
        try:
            date_obj = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format.", category="error")
            return redirect(url_for('views.add_experiment'))
        
        new_experiment = Experiment(
            title=title,
            description=request.form.get('description'),
            participant_count=int(request.form.get('participants') or 0),
            duration=int(request.form.get('duration') or 0),
            date=date_obj,
            tags=request.form.get('tags'),
            status="Completed"
        )
        db.session.add(new_experiment)
        db.session.commit()
        flash("Experiment added successfully!", category="success")
        return redirect(url_for('views.experiments'))
    
    return render_template("add-experiment.html", user=current_user)

@views.route('/experiments/<int:experiment_id>')
@login_required
def view_experiment(experiment_id):
    experiment = Experiment.query.get_or_404(experiment_id)
    nlp_analysis = experiment.nlp_analysis
    tracking_analysis = experiment.tracking_analysis
    
    emotion_data = nlp_analysis.emotion_data if nlp_analysis else None
    transcript_summary = nlp_analysis.transcript_summary if nlp_analysis else None
    
    timeline_preview = []
    questions_preview = []
    keywords_preview = []
    
    has_transcription = nlp_analysis is not None
    has_tracking = tracking_analysis is not None and tracking_analysis.detections is not None
    
    if nlp_analysis:
        timeline_preview = nlp_analysis.timeline_segments.order_by(TimelineSegment.start_time).limit(10).all()
        questions_preview = nlp_analysis.questions.limit(5).all()
        keywords_preview = nlp_analysis.keywords.order_by(Keyword.rank).limit(10).all()

    return render_template("single-experiment.html", 
                           user=current_user,
                           experiment=experiment,
                           nlp_analysis=nlp_analysis,
                           tracking_analysis=tracking_analysis,
                           emotion_data=emotion_data,
                           transcript_summary=transcript_summary,
                           timeline_preview=timeline_preview,
                           questions_preview=questions_preview,
                           keywords_preview=keywords_preview,
                           has_transcription=has_transcription,
                           has_tracking=has_tracking)

@views.route('/speech-to-text')
@login_required
def speech_to_text():
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    selected_exp_id = request.args.get('exp_id', type=int)
    
    selected_experiment = Experiment.query.get(selected_exp_id) if selected_exp_id else (all_experiments[0] if all_experiments else None)
    nlp_analysis = selected_experiment.nlp_analysis if selected_experiment else None

    # Default empty values
    timeline_data = []
    keywords_data = []
    questions_data = []
    highlights_data = []
    action_items_data = []
    complex_segments_data = []
    stats_data = {}
    
    if nlp_analysis:
        timeline_data = nlp_analysis.timeline_segments.order_by(TimelineSegment.start_time).all()
        keywords_data = nlp_analysis.keywords.order_by(Keyword.rank).limit(15).all()
        questions_data = nlp_analysis.questions.order_by(DetectedQuestion.position_index).all()

        if nlp_analysis.text_insights:
            ti = nlp_analysis.text_insights
            
            # Key Highlights
            raw_highlights = ti.important_sentences
            if isinstance(raw_highlights, str): raw_highlights = json.loads(raw_highlights)
            highlights_data = raw_highlights[:5] if raw_highlights else []

            # Action Items
            raw_actions = ti.action_items
            if isinstance(raw_actions, str): raw_actions = json.loads(raw_actions)
            action_items_data = raw_actions if raw_actions else []

            # Multi-Emotion Segments
            raw_complex = ti.multi_emotion_segments
            if isinstance(raw_complex, str): raw_complex = json.loads(raw_complex)
            complex_segments_data = raw_complex if raw_complex else []

            # Stats
            diversity = nlp_analysis.lexical_diversity or 0
            stats_data = {
                "word_count": nlp_analysis.word_count,
                "unique_words": nlp_analysis.unique_words_count,
                "diversity": round(diversity, 2),
                "complexity_score": min(int(diversity * 100 * 2.5), 100),
                "avg_sentence_len": ti.avg_sentence_length
            }

    return render_template(
        "speech-to-text.html", 
        user=current_user,
        experiments=all_experiments,
        selected_experiment=selected_experiment,
        nlp_analysis=nlp_analysis,
        timeline=timeline_data,
        keywords=keywords_data,
        questions=questions_data,
        highlights=highlights_data,
        action_items=action_items_data,
        complex_segments=complex_segments_data,
        stats=stats_data
    )

@views.route("/manual-annotation")
@login_required
def manual_annotation():
    ensure_annotation_buckets()
    
    jobs = get_all_annotation_jobs()
    
    return render_template("manual-annotation.html", 
                           user=current_user,
                           pending=[j for j in jobs if j["status"] == "pending"],
                           in_progress=[j for j in jobs if j["status"] == "in_progress"], 
                           completed=[j for j in jobs if j["status"] == "completed"])

@views.route("/manual-annotation/job/<job_id>")
@login_required
def manual_annotation_job(job_id):
    status = get_job_status(job_id)
    if not status:
        flash("Job not found", category="error")
        return redirect(url_for("views.manual_annotation"))
    
    all_groups = status.get("groups", [])
    labeled = set(status.get("labeled_groups", []))
    unlabeled = [g for g in all_groups if g["group_id"] not in labeled]
    
    if not unlabeled:
        status["status"] = "completed"
        status["completed_at"] = datetime.now().isoformat()
        save_job_status(job_id, status)
        flash("Job completed!", category="success")
        return redirect(url_for("views.manual_annotation"))
    
    current_group = unlabeled[0]
    
    # Get Images for group
    images = []
    try:
        client = get_minio_client()
        prefix = f"{job_id}/{current_group['group_id']}/"
        objects = client.list_objects(RAW_CROPS_BUCKET, prefix=prefix, recursive=True)
        all_images = [obj.object_name for obj in objects if obj.object_name.lower().endswith(('.jpg', '.jpeg', '.png'))]
        images = random.sample(all_images, 15) if len(all_images) > 15 else all_images
    except Exception:
        pass

    total = len(status.get("groups", []))
    done = len(status.get("labeled_groups", []))
    
    return render_template("manual-annotation-label.html",
                           user=current_user,
                           job_id=job_id,
                           job=status,
                           group=current_group,
                           images=images,
                           person_ids=list(range(1, status.get("participant_count", 6) + 1)),
                           progress=int((done / total) * 100) if total > 0 else 0,
                           done=done,
                           total=total)

@views.route("/manual-annotation/image/<path:image_path>")
@login_required
def annotation_serve_image(image_path):
    try:
        client = get_minio_client()
        response = client.get_object(RAW_CROPS_BUCKET, image_path)
        return send_file(BytesIO(response.read()), mimetype="image/jpeg")
    except Exception:
        return "Image not found", 404
    
@views.route("/detection-tracking")
@login_required
def detection_tracking():
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    selected_exp_id = request.args.get('exp_id', type=int)
    
    selected_experiment = Experiment.query.get(selected_exp_id) if selected_exp_id else (all_experiments[0] if all_experiments else None)
    
    nlp_analysis = selected_experiment.nlp_analysis if selected_experiment else None
    tracking_analysis = selected_experiment.tracking_analysis if selected_experiment else None
    
    stats = {
        'total_experiments': len(all_experiments),
        'experiments_with_transcription': sum(1 for exp in all_experiments if exp.has_transcription_data),
        'experiments_with_tracking': sum(1 for exp in all_experiments if exp.has_tracking_data),
        'total_participants': db.session.query(func.sum(Experiment.participant_count)).scalar() or 0,
        'avg_participants': round(db.session.query(func.avg(Experiment.participant_count)).scalar() or 0, 1),
        'completed_experiments': Experiment.query.filter_by(status='Completed').count(),
    }
        
    recent_activity = Experiment.query.order_by(Experiment.date.desc()).limit(5).all()
    trend_data = Experiment.query.order_by(Experiment.date.asc()).limit(6).all()
    
    participant_trend = {
        'labels': [exp.title[:15] + '...' if len(exp.title) > 15 else exp.title for exp in trend_data],
        'data': [exp.participant_count or 0 for exp in trend_data]
    }
    
    tags_query = db.session.query(Experiment.tags).filter(Experiment.tags.isnot(None)).all()
    tag_counts = {}
    for (tags_str,) in tags_query:
        if tags_str:
            for tag in tags_str.split(','):
                tag_counts[tag.strip()] = tag_counts.get(tag.strip(), 0) + 1
    
    top_experiments = Experiment.query.order_by(Experiment.participant_count.desc()).limit(10).all()
    
    return render_template("detection-tracking.html", 
                           user=current_user,
                           experiments=all_experiments,
                           selected_experiment=selected_experiment,
                           analysis=nlp_analysis,
                           nlp_analysis=nlp_analysis,
                           tracking_analysis=tracking_analysis,
                           stats=stats,
                           recent_activity=recent_activity,
                           tag_counts=tag_counts,
                           participant_trend=participant_trend,
                           top_experiments=top_experiments)


# API Routes
@views.route('/api/experiment/<int:exp_id>/status', methods=['POST'])
@login_required
def update_experiment_status(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    data = request.json
    new_status = data.get('status')
    
    if new_status in ['Completed', 'Archived']:
        experiment.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'new_status': new_status})
    
    return jsonify({'error': 'Invalid status'}), 400

@views.route("/api/experiment/<int:exp_id>/analysis")
@login_required
def get_experiment_analysis(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    nlp_analysis = experiment.nlp_analysis

    if not nlp_analysis:
        return jsonify({"error": "No nlp_analysis found"}), 404
    
    emotion_data = nlp_analysis.emotion_data  
    return jsonify({
        'id': nlp_analysis.id,
        'source': nlp_analysis.source_filename,
        'generated_at': nlp_analysis.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'analyzed_at': nlp_analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S') if nlp_analysis.analyzed_at else None,
        'total_segments': nlp_analysis.total_segments,
        'dominant_emotion': nlp_analysis.dominant_emotion,
        'emotion_percentages': emotion_data.emotion_percentages if emotion_data else {},  
        'emotion_counts': emotion_data.emotion_counts if emotion_data else {},  
        'timeline_points': nlp_analysis.timeline_segments.count(),
        'questions_detected': nlp_analysis.questions.count(),
        'actions_detected': nlp_analysis.actions.count(),
        'word_count': nlp_analysis.word_count,
        'reading_time': nlp_analysis.reading_time_minutes
    })

@views.route("/api/experiment/<int:exp_id>/timeline")
@login_required
def get_experiment_timeline(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    analysis = experiment.analysis

    if not analysis:
        return jsonify({"error": "No analysis found"}), 404
    
    segments = analysis.timeline_segments.order_by(TimelineSegment.start_time).all()
    timeline_data = [{
        'time': seg.start_time,
        'emotion': seg.primary_emotion,
        'confidence': seg.confidence_score,
        'sentiment': seg.sentiment_label,
        'text': seg.text_content[:100] if seg.text_content else ''
    } for seg in segments]
    
    return jsonify({'timeline': timeline_data})

@views.route("/api/experiment/<int:exp_id>/keywords")
@login_required
def get_experiment_keywords(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    analysis = experiment.analysis
    
    if not analysis:
        return jsonify({"error": "No analysis found"}), 404
    
    keywords = analysis.keywords.order_by(Keyword.rank.asc()).limit(20).all()
    
    return jsonify({
        'keywords': [{'word': k.text, 'count': k.value, 'score': k.relevance_score} for k in keywords],
        'total_words': analysis.word_count or 0,
        'unique_words': analysis.unique_words_count or 0
    })

@views.route('/api/experiment/<int:exp_id>/tracking_data')
@login_required
def get_tracking_data(exp_id):
    try:
        experiment = Experiment.query.get_or_404(exp_id)
        tracking = experiment.tracking_analysis
        
        response_data = {"people": []}

        if tracking and tracking.detections:
            response_data = dict(tracking.detections)
        
        if experiment.duration_seconds:
            response_data['video_duration_seconds'] = experiment.duration_seconds
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin sync routes
@views.route('/admin/sync-minio', methods=['POST'])
@login_required
def manual_sync():
    """Manual trigger for MinIO sync."""
    try:
        from sync.minio_sync import sync_new_analyses
        result = sync_new_analyses(max_imports=None)
        
        summary = f"Sync complete ({result.get('duration', 0):.1f}s): "
        details = f"{result.get('new_imports', 0)} new imports, {result.get('skipped', 0)} skipped."
        
        if result.get('errors', 0) > 0:
            flash(f"{summary} {details} Warning: {result['errors']} errors occurred.", category="warning")
        else:
            flash(f"{summary} {details}", category="success")

    except Exception as e:
        traceback.print_exc()
        flash(f"Sync failed to initialize: {str(e)}", category="error")
    
    target = request.referrer if request.referrer and request.host in request.referrer else url_for('views.experiments')
    return redirect(target)


# --- Annotation API Endpoints ---

@views.route("/api/annotation/jobs")
def annotation_list_jobs():
    """API endpoint to list all jobs (e.g., for external sensors)"""
    jobs = get_all_annotation_jobs()
    return jsonify(jobs)

@views.route("/api/annotation/job-status/<job_id>")
@login_required
def annotation_job_status(job_id):
    status = get_job_status(job_id)
    if not status:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(status)

@views.route("/api/annotation/set-participants", methods=["POST"])
@login_required
def annotation_set_participants():
    data = request.json
    job_id = data.get("job_id")
    count = data.get("count")
    
    if not job_id or not count:
        return jsonify({"error": "Missing data"}), 400
        
    status = get_job_status(job_id)
    if status:
        status["participant_count"] = int(count)
        if "experiment_name" not in status:
            status["experiment_name"] = job_id 
        save_job_status(job_id, status)
        
        # Update metadata file in tastelab-videos-sorted bucket
        if status.get("experiment_name"):
            update_session_metadata(status["experiment_name"], {
                "participant_count": int(count),
                "labeling_updated_at": datetime.now().isoformat()
            })
        
        return jsonify({"success": True})
    
    return jsonify({"error": "Job not found"}), 404

@views.route("/api/annotation/rename", methods=["POST"])
@login_required
def annotation_rename_job():
    data = request.json
    job_id = data.get("job_id")
    new_name = data.get("name", "").strip()
    
    status = get_job_status(job_id)
    if status and new_name:
        status["experiment_name"] = new_name
        save_job_status(job_id, status)
        return jsonify({"success": True, "name": new_name})
    
    return jsonify({"error": "Missing data or Job not found"}), 400

@views.route("/api/annotation/assign", methods=["POST"])
@login_required
def annotation_assign():
    data = request.json
    job_id = data.get("job_id")
    group_id = data.get("group_id")
    person_id = data.get("person_id")
    
    if not all([job_id, group_id, person_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    copied = copy_images_to_labeled(job_id, group_id, person_id, max_images=250)
    copied_count = len(copied)

    # Update Status
    status = get_job_status(job_id)
    if status:
        if "labeled_groups" not in status:
            status["labeled_groups"] = []
            
        if group_id not in status["labeled_groups"]:
            status["labeled_groups"].append(group_id)
            
        status["status"] = "in_progress"
        status["last_updated"] = datetime.now().isoformat()
        
        if "assignments" not in status:
            status["assignments"] = {}
        status["assignments"][group_id] = {
            "person_id": person_id,
            "timestamp": datetime.now().isoformat(),
            "images_copied": copied_count
        }
        
        save_job_status(job_id, status)
    
    return jsonify({"success": True, "copied": copied_count})

@views.route("/api/annotation/undo", methods=["POST"])
@login_required
def annotation_undo():
    data = request.json
    job_id = data.get("job_id")
    
    status = get_job_status(job_id)
    if status and status.get("labeled_groups"):
        last_group = status["labeled_groups"].pop()
        if "assignments" in status and last_group in status["assignments"]:
            del status["assignments"][last_group]
        
        save_job_status(job_id, status)
        return jsonify({"success": True, "undone_group": last_group})
    
    return jsonify({"error": "Nothing to undo"}), 400

@views.route("/api/annotation/skip", methods=["POST"])
@login_required
def annotation_skip():
    """Skip a group - move images to skipped folder."""
    data = request.json
    job_id = data.get("job_id")
    group_id = data.get("group_id")
    
    if not job_id or not group_id:
        return jsonify({"error": "Missing job_id or group_id"}), 400
    
    status = get_job_status(job_id)
    if not status:
        return jsonify({"error": "Job not found"}), 404
    
    client = get_minio_client()
    prefix = f"{job_id}/{group_id}/"
    moved = 0
    
    try:
        objects = list(client.list_objects(RAW_CROPS_BUCKET, prefix=prefix, recursive=True))
        for obj in objects:
            if obj.object_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                response = client.get_object(RAW_CROPS_BUCKET, obj.object_name)
                data_bytes = response.read()
                filename = obj.object_name.split('/')[-1]
                
                dest_path = f"skipped/{group_id}_{filename}"
                client.put_object(
                    LABELED_BUCKET,
                    dest_path,
                    BytesIO(data_bytes),
                    len(data_bytes),
                    content_type="image/jpeg"
                )
                moved += 1
    except Exception as e:
        print(f"Error moving skipped images: {e}")
    
    # Update status
    if "labeled_groups" not in status:
        status["labeled_groups"] = []
    if "skipped_groups" not in status:
        status["skipped_groups"] = []
    
    if group_id not in status["labeled_groups"]:
        status["labeled_groups"].append(group_id)
    if group_id not in status["skipped_groups"]:
        status["skipped_groups"].append(group_id)
    
    status["status"] = "in_progress"
    status["last_updated"] = datetime.now().isoformat()
    
    save_job_status(job_id, status)
    
    return jsonify({"success": True, "moved": moved})

@views.route("/api/annotation/toggle-staff", methods=["POST"])
@login_required
def annotation_toggle_staff():
    """Toggle staff status for a person."""
    data = request.json
    job_id = data.get("job_id")
    person_id = data.get("person_id")
    
    if not job_id or not person_id:
        return jsonify({"error": "Missing job_id or person_id"}), 400
    
    status = get_job_status(job_id)
    if not status:
        return jsonify({"error": "Job not found"}), 404
    
    if "staff" not in status:
        status["staff"] = []
    
    person_id = str(person_id)
    if person_id in status["staff"]:
        status["staff"].remove(person_id)
        is_staff = False
    else:
        status["staff"].append(person_id)
        is_staff = True
    
    save_job_status(job_id, status)
    
    return jsonify({"success": True, "person_id": person_id, "is_staff": is_staff})