
import json
from datetime import datetime
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from werkzeug.security import check_password_hash

from models import (db, User, Experiment, NlpAnalysis, TimelineSegment, Keyword,
                    TrackingAnalysis, ChartBin, DetectedQuestion)

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    selected_exp_id = request.args.get('exp_id', type=int)

    selected_experiment = (
        Experiment.query.get(selected_exp_id) if selected_exp_id
        else (all_experiments[0] if all_experiments else None)
    )

    nlp_analysis = selected_experiment.nlp_analysis if selected_experiment else None
    tracking_analysis = selected_experiment.tracking_analysis if selected_experiment else None

    avg_duration_sec = db.session.query(func.avg(Experiment.duration_seconds)).scalar() or 0
    total_duration_sec = db.session.query(func.sum(Experiment.duration_seconds)).scalar() or 0

    stats = {
        'total_experiments': Experiment.query.count(),
        'total_participants': db.session.query(func.sum(Experiment.participant_count)).scalar() or 0,
        'avg_participants': round(db.session.query(func.avg(Experiment.participant_count)).scalar() or 0, 1),
        'avg_duration': int(avg_duration_sec / 60),
        'completed_experiments': Experiment.query.count(),
        'this_month': Experiment.query.filter(
            Experiment.date >= datetime.now().replace(day=1, hour=0, minute=0, second=0)
        ).count()
    }

    recent_activity = Experiment.query.order_by(Experiment.date.desc()).limit(5).all()
    trend_data = Experiment.query.order_by(Experiment.date.asc()).all()

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

    tags_query = db.session.query(Experiment.tags).filter(Experiment.tags.isnot(None)).all()
    all_tags = set()
    for (tags_str,) in tags_query:
        if tags_str:
            all_tags.update([t.strip() for t in tags_str.split(',') if t.strip()])

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

    selected_experiment = (
        Experiment.query.get(selected_exp_id) if selected_exp_id
        else (all_experiments[0] if all_experiments else None)
    )
    nlp_analysis = selected_experiment.nlp_analysis if selected_experiment else None

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

            raw_highlights = ti.important_sentences
            if isinstance(raw_highlights, str): raw_highlights = json.loads(raw_highlights)
            highlights_data = raw_highlights[:5] if raw_highlights else []

            raw_actions = ti.action_items
            if isinstance(raw_actions, str): raw_actions = json.loads(raw_actions)
            action_items_data = raw_actions if raw_actions else []

            raw_complex = ti.multi_emotion_segments
            if isinstance(raw_complex, str): raw_complex = json.loads(raw_complex)
            complex_segments_data = raw_complex if raw_complex else []

            diversity = nlp_analysis.lexical_diversity or 0
            stats_data = {
                "word_count": nlp_analysis.word_count,
                "unique_words": nlp_analysis.unique_words_count,
                "diversity": round(diversity, 2),
                "complexity_score": min(int(diversity * 100 * 2.5), 100),
                "avg_sentence_len": ti.avg_sentence_length
            }

    return render_template("speech-to-text.html",
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
                           stats=stats_data)


@views.route("/detection-tracking")
@login_required
def detection_tracking():
    all_experiments = Experiment.query.order_by(Experiment.date.desc()).all()
    selected_exp_id = request.args.get('exp_id', type=int)

    selected_experiment = (
        Experiment.query.get(selected_exp_id) if selected_exp_id
        else (all_experiments[0] if all_experiments else None)
    )

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