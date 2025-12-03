from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash
from sqlalchemy import func
from datetime import datetime
from models import (
    db, User, Experiment, NlpAnalysis, EmotionSummary, 
    TimelineSegment, ChartBin, DetectedQuestion, DetectedAction, 
    Keyword, TopicSentiment, TextInsight, TranscriptSummary
)

# Create blueprint
views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    # Get all experiments (which may have analysis data linked)
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    
    # Get selected experiment from URL params
    selected_exp_id = request.args.get('exp_id', type=int)
    selected_experiment = None
    
    if selected_exp_id:
        selected_experiment = Experiment.query.get(selected_exp_id)
    elif all_experiments:
        selected_experiment = all_experiments[0]
    
    # Get analysis data if available
    analysis = None
    if selected_experiment:
        analysis = selected_experiment.analysis
    
    # --- Statistics for Dashboard ---
    stats = {
        'total_experiments': Experiment.query.count(),
        'experiments_with_analysis': NlpAnalysis.query.filter(NlpAnalysis.experiment_id.isnot(None)).count(),
        'total_participants': db.session.query(func.sum(Experiment.participant_count)).scalar() or 0,
        'avg_participants': round(db.session.query(func.avg(Experiment.participant_count)).scalar() or 0, 1),
        'completed_experiments': Experiment.query.filter_by(status='Completed').count(),
        'total_segments': db.session.query(func.sum(NlpAnalysis.total_segments)).scalar() or 0
    }
    
    # Recent activity list
    recent_activity = Experiment.query.order_by(Experiment.date.desc()).limit(5).all()
    
    # Tag distribution
    tags_query = db.session.query(Experiment.tags).filter(Experiment.tags.isnot(None)).all()
    tag_counts = {}
    for (tags_str,) in tags_query:
        if tags_str:
            tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            for tag in tags_list:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Participant trends (Timeline Chart)
    trend_data = Experiment.query.order_by(Experiment.date.asc()).limit(6).all()
    participant_trend = {
        'labels': [exp.title[:15] + '...' if len(exp.title) > 15 else exp.title for exp in trend_data],
        'data': [exp.participant_count or 0 for exp in trend_data]
    }
    
    # Insights box
    insights = {
        'avg_duration': int(db.session.query(func.avg(Experiment.duration)).scalar() or 0),
        'total_duration': db.session.query(func.sum(Experiment.duration)).scalar() or 0,
        'this_month': Experiment.query.filter(
            Experiment.date >= datetime.now().replace(day=1, hour=0, minute=0, second=0)
        ).count(),
        'last_experiment': all_experiments[0] if all_experiments else None
    }
    
    top_experiments = Experiment.query.order_by(
        Experiment.participant_count.desc()
    ).limit(10).all()
    
    return render_template("home.html", 
                           user=current_user,
                           experiments=all_experiments,
                           selected_experiment=selected_experiment,
                           analysis=analysis,
                           stats=stats,
                           recent_activity=recent_activity,
                           tag_counts=tag_counts,
                           participant_trend=participant_trend,
                           insights=insights,
                           top_experiments=top_experiments)


@views.route("/experiments")
@login_required
def experiments():
    recent_experiments = Experiment.query.order_by(Experiment.date.desc()).limit(6).all()
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    archived_experiments = Experiment.query.filter_by(status="Archived").order_by(Experiment.date.desc()).all()
    
    # Extract unique tags
    tags_query = db.session.query(Experiment.tags).filter(Experiment.tags.isnot(None)).all()
    all_tags = set()
    for (tags_str,) in tags_query:
        if tags_str:
            tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            all_tags.update(tags_list)
    unique_tags = sorted(list(all_tags))

    return render_template("experiments.html",
                           user=current_user,
                           recent_experiments=recent_experiments,
                           all_experiments=all_experiments,
                           archived_experiments=archived_experiments,
                           tags=unique_tags)


@views.route('/experiments/add-experiment', methods=['GET', 'POST'])
@login_required
def add_experiment():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        participants = request.form.get('participants')
        duration = request.form.get('duration')
        date_str = request.form.get('date')
        tags = request.form.get('tags')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format.", category="error")
            return redirect(url_for('views.add_experiment'))
        
        existing_exp = Experiment.query.filter_by(title=title).first()
        if existing_exp:
            flash("An experiment with this title already exists.", category="error")
            return redirect(url_for('views.add_experiment'))
        
        new_experiment = Experiment(
            title=title,
            description=description,
            participant_count=int(participants) if participants else 0,
            duration=int(duration) if duration else 0,
            date=date_obj,
            tags=tags if tags else None,
            avg_score=0.0,
            status="Completed"
        )
        
        db.session.add(new_experiment)
        db.session.commit()
        
        flash("Experiment added successfully! You can now import emotion analysis data for this experiment.", category="success")
        return redirect(url_for('views.experiments'))
    
    return render_template("add-experiment.html", user=current_user)


@views.route('/experiments/<int:experiment_id>')
@login_required
def view_experiment(experiment_id):
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # Get analysis results linked to this experiment
    analysis = experiment.analysis
    
    summary = None
    timeline_preview = []
    questions_preview = []
    keywords_preview = []
    
    if analysis:
        summary = analysis.emotion_summary
        timeline_preview = (analysis.timeline_segments
                            .order_by(TimelineSegment.start_time)
                            .limit(10)
                            .all())
        questions_preview = analysis.questions.limit(5).all()
        keywords_preview = analysis.keywords.order_by(Keyword.rank).limit(10).all()

    return render_template("single-experiment.html", 
                           user=current_user,
                           experiment=experiment,
                           analysis=analysis,
                           summary=summary,
                           timeline_preview=timeline_preview,
                           questions_preview=questions_preview,
                           keywords_preview=keywords_preview)


@views.route('/transcription')
@login_required
def transcription():
    """
    Emotion Analysis Dashboard - Shows experiments with analysis data
    """
    # Get all experiments that have analysis data
    experiments_with_analysis = Experiment.query.join(NlpAnalysis).order_by(
        Experiment.date.desc()
    ).all()

    # Determine selected experiment
    selected_experiment = None
    analysis = None
    timeline_data = []
    summary_data = None
    keywords_data = []
    
    exp_id = request.args.get('id')

    if exp_id:
        selected_experiment = Experiment.query.get(exp_id)
        if selected_experiment:
            analysis = selected_experiment.analysis
    elif experiments_with_analysis:
        selected_experiment = experiments_with_analysis[0]
        analysis = selected_experiment.analysis

    # Prepare detailed data
    if analysis:
        summary_data = analysis.emotion_summary
        timeline_data = (analysis.timeline_segments
                         .order_by(TimelineSegment.start_time)
                         .all())
        keywords_data = (analysis.keywords
                        .order_by(Keyword.rank)
                        .limit(20)
                        .all())

    return render_template(
        "transcription.html", 
        user=current_user,
        experiments=experiments_with_analysis,
        selected_experiment=selected_experiment,
        analysis=analysis,
        timeline=timeline_data,
        summary=summary_data,
        keywords=keywords_data
    )

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


@views.route("/api/experiment/<int:exp_id>/analysis")
@login_required
def get_experiment_analysis(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    analysis = experiment.analysis

    if not analysis:
        return jsonify({"error": "No analysis found"}), 404
    
    summary = analysis.emotion_summary
    
    return jsonify({
        'id': analysis.id,
        'source': analysis.source_filename,
        'generated_at': analysis.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'analyzed_at': analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.analyzed_at else None,
        'total_segments': analysis.total_segments,
        'dominant_emotion': analysis.dominant_emotion,
        'emotion_percentages': summary.emotion_percentages if summary else {},
        'emotion_counts': summary.emotion_counts if summary else {},
        'timeline_points': analysis.timeline_segments.count(),
        'questions_detected': analysis.questions.count(),
        'actions_detected': analysis.actions.count(),
        'word_count': analysis.word_count,
        'reading_time': analysis.reading_time_minutes
    })

@views.route("/api/experiment/<int:exp_id>/timeline")
@login_required
def get_experiment_timeline(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    analysis = experiment.analysis

    if not analysis:
        return jsonify({"error": "No analysis found"}), 404
    
    segments = analysis.timeline_segments.order_by(TimelineSegment.start_time).all()
    
    timeline_data = []
    for seg in segments:
        timeline_data.append({
            'time': seg.start_time,
            'emotion': seg.primary_emotion,
            'confidence': seg.confidence_score,
            'sentiment': seg.sentiment_label,
            'text': seg.text_content[:100] if seg.text_content else ''
        })
    
    return jsonify({'timeline': timeline_data})

@views.route("/api/experiment/<int:exp_id>/charts")
@login_required
def get_experiment_charts(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    analysis = experiment.analysis

    if not analysis:
        return jsonify({"error": "No analysis found"}), 404
    
    summary = analysis.emotion_summary
    
    timeline_data = []
    segments = analysis.timeline_segments.order_by(TimelineSegment.start_time).all()
    
    for seg in segments:
        timeline_data.append({
            'time': seg.start_time,
            'emotion': seg.primary_emotion,
            'confidence': seg.confidence_score
        })
    
    return jsonify({
        'emotion_distribution': summary.emotion_percentages if summary else {},
        'timeline': timeline_data,
        'primary_emotions': summary.primary_emotion_counts if summary else {}
    })

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

@views.route("/api/experiment/<int:exp_id>")
@login_required
def get_experiment_metadata(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    
    return jsonify({
        'id': experiment.id,
        'title': experiment.title,
        'date': experiment.date.strftime('%B %d, %Y'),
        'participants': experiment.participant_count or 0,
        'duration': experiment.format_duration(),
        'status': experiment.status,
        'has_analysis': experiment.analysis is not None,
        'analysis_id': experiment.analysis.id if experiment.analysis else None
    })

@views.route("/analytics")
@login_required
def analytics():
    """Advanced analytics page showing all analysis results"""
    
    # Get all experiments with analysis
    experiments_with_analysis = Experiment.query.join(NlpAnalysis).order_by(
        Experiment.date.desc()
    ).all()
    
    emotion_aggregates = {}
    total_segments = 0
    
    for exp in experiments_with_analysis:
        analysis = exp.analysis
        summary = analysis.emotion_summary
        if summary and summary.emotion_percentages:
            for emotion, percentage in summary.emotion_percentages.items():
                emotion_aggregates[emotion] = emotion_aggregates.get(emotion, 0) + percentage
            total_segments += analysis.total_segments or 0
    
    if experiments_with_analysis:
        for emotion in emotion_aggregates:
            emotion_aggregates[emotion] /= len(experiments_with_analysis)
    
    return render_template("analytics.html", 
                           user=current_user,
                           experiments=experiments_with_analysis,
                           emotion_aggregates=emotion_aggregates,
                           total_segments=total_segments)

@views.route("/detection-tracking")
@login_required
def detection_tracking():
    return render_template("detection-tracking.html", user=current_user)

@views.route('/admin/sync-minio', methods=['POST'])
@login_required
def manual_sync():
    """Manual trigger for MinIO sync"""
    try:
        from sync.minio_sync import sync_new_analyses
        # Call without max_imports to import all available files
        result = sync_new_analyses(max_imports=None)
        
        message = (f"Sync complete in {result['duration']}s: "
                  f"{result['new_imports']} new analyses imported, "
                  f"{result['skipped']} already exist")
        
        if result['errors'] > 0:
            message += f", {result['errors']} errors (check logs)"
        
        flash(message, category="success" if result['errors'] == 0 else "warning")
        
    except Exception as e:
        flash(f"Sync failed: {str(e)}", category="error")
        import traceback
        print(traceback.format_exc())
    
    return redirect(request.referrer or url_for('views.experiments'))