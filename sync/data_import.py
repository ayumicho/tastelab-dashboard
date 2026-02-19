import re
from datetime import datetime
from main import app
from models import (
    db, NlpAnalysis, EmotionData, TimelineSegment, ChartBin,
    TranscriptSummary, Keyword, TopicSentiment, DetectedQuestion,
    DetectedAction, TextInsight, Experiment, TrackingAnalysis
)
from db_names import Columns


def find_or_create_experiment(video_name, date_folder, session_folder):
    """
    Find or create an experiment record based on session metadata.
    
    This function attempts to find an existing experiment by partial match,
    then exact match. If not found, creates a new experiment from the session
    folder name and date.
    
    Args:
        video_name (str): Name of the video file
        date_folder (str): Date folder in format YYYY-MM-DD
        session_folder (str): Session folder name (e.g., "muffin_taste_test_1200")
    
    Returns:
        Experiment: Existing or newly created experiment record
    
    """

    # Clean the folder name to generate a readable title
    # e.g., "muffin_taste_test_1200" -> "Muffin Taste Test"
    name_without_time = re.sub(r'_\d{4}$', '', session_folder)
    clean_name = name_without_time.replace('_', ' ').title()

    # Find experiment with exact name 
    exp = Experiment.query.filter(
        getattr(Experiment, Columns.TITLE).ilike(clean_name)
    ).first()
    
    if exp:
        print(f"Found experiment by exact match: '{exp.title}'")
        return exp
    
    # If no match found, create new experiment
    try:
        date_parts = date_folder.split('-')
        if len(date_parts) == 3:
            experiment_date = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        else:
            experiment_date = datetime.now()
    except ValueError:
        experiment_date = datetime.now()
    
    new_exp = Experiment(
        title=clean_name,
        date=experiment_date,
        participant_count=0,
        duration=0,
        duration_seconds=0,
        status="No Analysis",
        tags=""
    )
    
    db.session.add(new_exp)
    db.session.flush()
    
    print(f"Created new experiment: '{clean_name}' (ID: {new_exp.id})")
    return new_exp

def insert_analysis_data(session_data, date_folder, session_folder, video_name):
    """
    Parse JSON session data and insert all analysis results into the database.
    
    This function handles five main data categories:
    1. Metadata (duration, participant count)
    2. Computer Vision (tracking and detection data)
    3. NLP Analysis (sentiment, transcription, emotions)
    4. Supplementary NLP data (keywords, topics, questions, actions)
    5. Text insights (complex moments, multi-emotion segments)
    
    Uses bulk operations for performance on large datasets.
    
    Args:
        session_data (dict): Complete session JSON data
        date_folder (str): Date folder in format YYYY-MM-DD
        session_folder (str): Session folder name
        video_name (str): Name of the video file
    
    Returns:
        int: Experiment ID on success, None on failure
    
    Raises:
        Exception: Any database or parsing errors are caught and logged
    """
    try:
        # Check for data availability
        has_sentiment = 'sentiment' in session_data
        has_insights = 'insights' in session_data
        has_chart = 'chart_data' in session_data
        has_keywords = 'keyword_cloud' in session_data
        has_summary = 'summary' in session_data
        has_detections = 'detections' in session_data
        has_metadata = 'metadata' in session_data
        has_transcript_base = 'transcript_base' in session_data
            
        sentiment_data = session_data.get('sentiment', {})
        insights_data = session_data.get('insights', {})
        chart_data = session_data.get('chart_data', {})
        keyword_data = session_data.get('keyword_cloud', {})
        summary_data = session_data.get('summary', {})
        detections = session_data.get('detections', {})
        metadata = session_data.get('metadata', {})
        transcript_base = session_data.get('transcript_base', {})
        base_segments = transcript_base.get('segments', [])

        experiment = find_or_create_experiment(video_name, date_folder, session_folder)

        # --- 1. Handle Metadata (Duration) ---
        if has_metadata:
            videos_list = metadata.get('videos', [])
            video_entry = next(
                (v for v in videos_list if v.get('new_filename') == f"{video_name}.mp4"), 
                None
            )

            if video_entry and 'duration_seconds' in video_entry:
                try:
                    raw_seconds = float(video_entry['duration_seconds'])
                    experiment.duration_seconds = raw_seconds
                    experiment.duration = int(raw_seconds / 60) 
                    db.session.add(experiment)
                    print(f"   -> Set Duration: {experiment.duration_seconds}s")
                except (ValueError, TypeError) as e:
                    print(f"   -> Warning: Could not parse duration: {e}")

        # --- 2. Generate Tags from Topics ---
        if has_insights and 'topics' in insights_data:
            topics_list_raw = insights_data.get('topics', [])
            topic_names = []
            
            for topic_item in topics_list_raw:
                if isinstance(topic_item, list) and len(topic_item) >= 1:
                    topic_names.append(topic_item[0])
                elif isinstance(topic_item, dict) and 'topic' in topic_item:
                    topic_names.append(topic_item['topic'])

            if topic_names:
                tags_str = ", ".join(topic_names)
                if len(tags_str) > 200:
                    tags_str = tags_str[:197] + "..."
                
                experiment.tags = tags_str
                db.session.add(experiment)
                print(f"   -> Generated Tags: {tags_str}")

        # --- 3. Handle Computer Vision Data (Tracking) ---
        if has_detections and 'people' in detections:
            unique_people = len(detections['people'])
            experiment.participant_count = unique_people
            print(f"   -> Updated Participant Count: {unique_people}")

            existing_tracking = TrackingAnalysis.query.filter_by(
                experiment_id=experiment.id
            ).first()

            if existing_tracking:
                print(f"   -> Updating existing TrackingAnalysis (ID: {existing_tracking.id})")
                existing_tracking.detections = detections
                existing_tracking.source_filename = video_name
            else:
                print(f"   -> Creating new TrackingAnalysis")
                new_tracking = TrackingAnalysis(
                    experiment_id=experiment.id,
                    source_filename=video_name,
                    detections=detections,
                    created_at=datetime.now()
                )
                db.session.add(new_tracking)

        # --- 4. Handle NLP Data (Sentiment & Transcription) ---
        analysis_id = None
        nlp_created_now = False

        # 1. Get or Create Parent NLP Record
        existing_nlp = NlpAnalysis.query.filter_by(experiment_id=experiment.id).first()

        if existing_nlp:
            print(f"   -> NLP Analysis exists (ID: {existing_nlp.id})")
            analysis_id = existing_nlp.id
            
        elif has_sentiment:
            sentiment_summary = sentiment_data.get('summary', {})
            nlp_analysis = NlpAnalysis(
                experiment_id=experiment.id,
                source_filename=video_name,
                generated_at=datetime.now(),
                analyzed_at=datetime.fromisoformat(sentiment_data.get('analyzed_at', datetime.now().isoformat())),
                model_used=sentiment_data.get('model_used', ''),
                total_segments=sentiment_summary.get('total_segments', 0),
                reading_time_minutes=insights_data.get('reading_time_minutes', 0.0),
                word_count=insights_data.get('counts', {}).get('words', 0),
                unique_words_count=insights_data.get('counts', {}).get('unique_words', 0),
                lexical_diversity=insights_data.get('lexical_diversity', 0.0),
                dominant_emotion=sentiment_summary.get('dominant_emotion', 'neutral')
            )
            db.session.add(nlp_analysis)
            db.session.flush() # Flush to generate ID for child tables
            analysis_id = nlp_analysis.id
            nlp_created_now = True
            print(f"   -> Created new NLP Analysis (ID: {analysis_id})")

        # 2. Handle Child Tables (Run this for BOTH new and existing records)
        if analysis_id:
            if nlp_created_now:
                sentiment_summary = sentiment_data.get('summary', {})
                
                # Emotion Overview
                emotion_data = EmotionData(
                    analysis_id=analysis_id,
                    emotion_percentages=sentiment_summary.get('emotion_percentages', {}),
                    emotion_counts=sentiment_summary.get('emotion_counts', {}),
                    primary_emotion_counts=sentiment_summary.get('primary_emotion_counts', {})
                )
                db.session.add(emotion_data)
                
                # Timeline Segments
                detailed_analyses = sentiment_data.get('detailed_analyses', [])
                timeline_segments_data = []
                
                for idx, segment in enumerate(detailed_analyses):
                    # Sync timestamps with transcript base if available
                    start_time = float(idx)
                    end_time = float(idx + 1)
                    
                    if has_transcript_base and idx < len(base_segments):
                        base_seg = base_segments[idx]
                        start_time = float(base_seg.get('start', start_time))
                        end_time = float(base_seg.get('end', end_time))
                
                    primary_emotion = segment.get('primary_emotion', segment.get('emotion', 'neutral'))
                    dialogue_emotions_raw = segment.get('dialogue_emotions', {})
                    sentiment_data_raw = segment.get('sentiment', {})
                    
                    # Normalize emotion vector
                    if isinstance(dialogue_emotions_raw, list):
                        emotion_vector = {item[0]: item[1] for item in dialogue_emotions_raw if len(item) == 2}
                    elif isinstance(dialogue_emotions_raw, dict):
                        emotion_vector = dialogue_emotions_raw
                    else:
                        emotion_vector = {}
                    
                    # Normalize sentiment score
                    if isinstance(sentiment_data_raw, dict):
                        sentiment_label = sentiment_data_raw.get('label', 'neutral')
                        sentiment_score = sentiment_data_raw.get('score', 0.0)
                    else:
                        sentiment_label = str(sentiment_data_raw) if sentiment_data_raw else 'neutral'
                        sentiment_score = 0.0
                    
                    confidence = emotion_vector.get(primary_emotion, 0.5) if emotion_vector else 0.5
                    
                    timeline_segments_data.append({
                        Columns.ANALYSIS_ID: analysis_id,
                        Columns.SEGMENT_INDEX: idx,
                        Columns.START_TIME: start_time,
                        Columns.END_TIME: end_time,
                        'duration': end_time - start_time,
                        Columns.TEXT_CONTENT: segment.get('text', ''),
                        Columns.PRIMARY_EMOTION: primary_emotion,
                        Columns.SENTIMENT_LABEL: sentiment_label,
                        Columns.SENTIMENT_SCORE: sentiment_score,
                        Columns.CONFIDENCE_SCORE: confidence,
                        Columns.EMOTION_VECTOR: emotion_vector if emotion_vector else None
                    })
                
                if timeline_segments_data:
                    db.session.bulk_insert_mappings(TimelineSegment, timeline_segments_data)
                
                # Chart Bins
                if has_chart and 'timeline' in chart_data:
                    timeline_bins = chart_data['timeline'].get('timeline_bins', [])
                    chart_bins_data = [
                        {
                            Columns.ANALYSIS_ID: analysis_id,
                            Columns.BIN_INDEX: b.get('bin_index', 0),
                            Columns.START_TIME: b.get('start_time', 0.0),
                            Columns.END_TIME: b.get('end_time', 0.0),
                            Columns.FORMATTED_START: b.get('formatted_start', ''),
                            Columns.FORMATTED_END: b.get('formatted_end', ''),
                            Columns.DOMINANT_EMOTION: b.get('dominant_emotion', 'neutral'),
                            Columns.EMOTION_COUNTS: b.get('emotion_counts', {}),
                            Columns.EMOTION_PERCENTAGES: b.get('emotion_percentages', {})
                        }
                        for b in timeline_bins
                    ]
                    
                    if chart_bins_data:
                        db.session.bulk_insert_mappings(ChartBin, chart_bins_data)
            
            # 1. Transcript Summary
            if has_summary:
                summary_missing = nlp_created_now or (
                    TranscriptSummary.query.filter_by(analysis_id=analysis_id).first() is None
                )
                
                if summary_missing:
                    transcript_sum = TranscriptSummary(
                        analysis_id=analysis_id,
                        summary=summary_data.get('summary', ''),
                        length_profile=summary_data.get('length_profile', 'medium'),
                        num_segments=summary_data.get('num_segments', 0)
                    )
                    db.session.add(transcript_sum)
            
            # 2. Keywords
            if has_keywords:
                keywords_missing = nlp_created_now or (
                    Keyword.query.filter_by(analysis_id=analysis_id).count() == 0
                )
                
                if keywords_missing:
                    kw_list = keyword_data if isinstance(keyword_data, list) else (keyword_data.get('keywords', []) or keyword_data.get('words', []))
                    keywords_data = [
                        {
                            Columns.ANALYSIS_ID: analysis_id,
                            Columns.TEXT: kw.get('text', ''),
                            Columns.RANK: idx + 1,
                            Columns.VALUE: kw.get('value', 0),
                            Columns.TF_IDF: kw.get('tf_idf_score', 0.0),
                            Columns.RELEVANCE_SCORE: kw.get('relevance_score', 0.0)
                        }
                        for idx, kw in enumerate(kw_list[:50])
                    ]
                    
                    if keywords_data:
                        db.session.bulk_insert_mappings(Keyword, keywords_data)

            # 3. Topic Sentiments
            if has_insights and 'topics' in insights_data:
                topics_missing = nlp_created_now or (
                    TopicSentiment.query.filter_by(analysis_id=analysis_id).count() == 0
                )
                
                if topics_missing:
                    topics = insights_data.get('topics', [])[:10]
                    topics_data = []
                    for topic_item in topics:
                        if isinstance(topic_item, list) and len(topic_item) >= 2:
                            topics_data.append({
                                Columns.ANALYSIS_ID: analysis_id,
                                Columns.TOPIC_NAME: topic_item[0],
                                Columns.TOTAL_SEGMENTS: topic_item[1],
                                Columns.DOMINANT_EMOTION: 'neutral',
                                Columns.AVERAGE_CONFIDENCE: 0.0,
                                Columns.EMOTION_DIVERSITY: 0.0,
                                Columns.TIME_SPAN_SECONDS: 0.0,
                                'sample_segments': []
                            })
                    
                    if topics_data:
                        db.session.bulk_insert_mappings(TopicSentiment, topics_data)

            # 4. Detected Questions
            if has_insights:
                questions_missing = nlp_created_now or (
                    DetectedQuestion.query.filter_by(analysis_id=analysis_id).count() == 0
                )
                
                if questions_missing:
                    sentiment_sum = insights_data.get('sentiment_summary', {})
                    questions_list = sentiment_sum.get('questions_detected', {}).get('questions_by_time', [])
                    questions_data = [
                        {
                            Columns.ANALYSIS_ID: analysis_id,
                            Columns.QUESTION_TEXT: q.get('question_text', ''),
                            Columns.PATTERN_MATCHED: q.get('pattern_matched', ''),
                            Columns.POSITION_INDEX: q.get('position', 0),
                            Columns.CONFIDENCE: q.get('confidence', 0.0)
                        }
                        for q in questions_list[:20] if isinstance(q, dict)
                    ]
                    
                    if questions_data:
                        db.session.bulk_insert_mappings(DetectedQuestion, questions_data)

            # 5. Detected Actions
            if has_insights:
                actions_missing = nlp_created_now or (
                    DetectedAction.query.filter_by(analysis_id=analysis_id).count() == 0
                )
                
                if actions_missing:
                    sentiment_sum = insights_data.get('sentiment_summary', {})
                    actions_list = sentiment_sum.get('action_items_detected', {}).get('actions_by_time', [])
                    actions_data = [
                        {
                            Columns.ANALYSIS_ID: analysis_id,
                            Columns.ACTION_TEXT: a.get('action_text', ''),
                            Columns.PATTERN_MATCHED: a.get('pattern_matched', ''),
                            Columns.POSITION_INDEX: a.get('position', 0),
                            Columns.CONFIDENCE: a.get('confidence', 0.0)
                        }
                        for a in actions_list[:20] if isinstance(a, dict)
                    ]
                    
                    if actions_data:
                        db.session.bulk_insert_mappings(DetectedAction, actions_data)

            # 6. Text Insight (Complex segments & Actions summary)
            if has_insights:
                insights_missing = nlp_created_now or (
                    TextInsight.query.filter_by(analysis_id=analysis_id).first() is None
                )
                
                if insights_missing:
                    text_stats = insights_data.get('text_statistics', {})
                    sentiment_sum = insights_data.get('sentiment_summary', {})
                    
                    # Consolidate Action Items
                    actions_source = sentiment_sum.get('action_items_detected', {})
                    raw_actions = actions_source.get('action_examples', []) or actions_source.get('actions_by_time', [])
                    action_items_list = [
                        a.get('action_text') for a in raw_actions 
                        if isinstance(a, dict) and a.get('action_text')
                    ]

                    # Consolidate Multi-Emotion Segments
                    multi_source = sentiment_sum.get('multi_emotion_segments', {})
                    multi_segments_list = [
                        {
                            'start_time': m.get('time'),
                            'text_snippet': m.get('text'),
                            'emotions': [e.get('emotion') for e in m.get('emotions', []) if e.get('emotion')]
                        }
                        for m in multi_source.get('examples', []) if isinstance(m, dict)
                    ]

                    text_insight = TextInsight(
                        analysis_id=analysis_id,
                        top_bigrams=insights_data.get('top_bigrams', []),
                        top_trigrams=insights_data.get('top_trigrams', []),
                        important_sentences=insights_data.get('important_sentences', []),
                        avg_sentence_length=text_stats.get('avg_sentence_length_tokens', 0.0),
                        avg_word_length=text_stats.get('avg_word_length', 0.0),
                        action_items=action_items_list,
                        multi_emotion_segments=multi_segments_list
                    )
                    db.session.add(text_insight)
                    
        # Commit all changes
        experiment.sync_from_analysis()
        db.session.commit()
        print(f"✓ Data import complete for Experiment: '{experiment.title}'")
        return experiment.id

    except Exception as e:
        db.session.rollback()
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return None