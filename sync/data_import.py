from datetime import datetime
from app import app
from models import (
    db, NlpAnalysis, EmotionSummary, TimelineSegment, ChartBin,
    TranscriptSummary, Keyword, TopicSentiment, DetectedQuestion,
    DetectedAction, TextInsight, Experiment
)
from db_names import Columns


def find_or_create_experiment(video_name, date_folder, session_folder):
    """
    Find existing experiment or create a new one.
    Uses constants from db_names.py
    """
    # Strategy 1: Try to find by exact title match
    clean_name = video_name.replace('_', ' ').title()
    exp = Experiment.query.filter(
        getattr(Experiment, Columns.TITLE).ilike(f"%{clean_name}%")
    ).first()
    
    if exp:
        app.logger.info(f"Found existing experiment: '{exp.title}'")
        return exp
    
    # Strategy 2: Try to find by date
    try:
        date_parts = date_folder.split('-')
        if len(date_parts) == 3:
            year, month, day = date_parts
            target_date = datetime(int(year), int(month), int(day))
            
            # Using Columns constant
            exp = Experiment.query.filter(
                db.func.date(getattr(Experiment, Columns.DATE)) == target_date.date()
            ).first()
            
            if exp:
                app.logger.info(f"Found experiment by date: '{exp.title}'")
                return exp
    except:
        pass
    
    # Strategy 3: Create a new experiment automatically
    app.logger.info(f"Creating new experiment from NLP analysis...")
    
    try:
        date_parts = date_folder.split('-')
        if len(date_parts) == 3:
            experiment_date = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        else:
            experiment_date = datetime.now()
    except:
        experiment_date = datetime.now()
    
    title = f"{session_folder.replace('_', ' ').title()} - {video_name.replace('_', ' ').title()}"
    
    # Create using normal ORM (this is fine, single record)
    new_exp = Experiment(
        title=title,
        description=f"Auto-generated from MinIO import: {video_name}",
        date=experiment_date,
        participant_count=0,
        duration=0,
        status="Completed",
        tags="Auto-imported"
    )
    
    db.session.add(new_exp)
    db.session.flush()
    
    app.logger.info(f"Created new experiment: '{title}' (ID: {new_exp.id})")
    return new_exp


def insert_analysis_data(session_data, date_folder, session_folder, video_name):
    """
    Insert all analysis data using BULK OPERATIONS with constants
    """
    try:
        has_sentiment = 'sentiment' in session_data
        has_insights = 'insights' in session_data
        has_chart = 'chart_data' in session_data
        has_keywords = 'keyword_cloud' in session_data
        has_summary = 'summary' in session_data
        
        app.logger.info(f"Files: sentiment={has_sentiment}, insights={has_insights}, "
                               f"chart={has_chart}, keywords={has_keywords}, summary={has_summary}")
        
        if not has_sentiment:
            app.logger.error("Cannot proceed without sentiment.json")
            return None
        
        sentiment_data = session_data['sentiment']
        insights_data = session_data.get('insights', {})
        chart_data = session_data.get('chart_data', {})
        keyword_data = session_data.get('keyword_cloud', {})
        summary_data = session_data.get('summary', {})
        
        # Find or create an experiment
        experiment = find_or_create_experiment(video_name, date_folder, session_folder)
        
        # Check if this experiment already has analysis
        existing_analysis = NlpAnalysis.query.filter_by(
            **{Columns.EXPERIMENT_ID: experiment.id}
        ).first()
        
        if existing_analysis:
            app.logger.info(f"Experiment already has analysis (ID: {existing_analysis.id})")
            app.logger.info(f"Skipping to avoid duplicates...")
            return existing_analysis.id
        
        # 1. Create NlpAnalysis (root) - single record, use ORM
        sentiment_summary = sentiment_data.get('summary', {})
        
        analysis = NlpAnalysis(
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
        db.session.add(analysis)
        db.session.flush()  # Get analysis.id
        app.logger.info(f"Created NlpAnalysis (ID: {analysis.id})")
        
        # 2. Create EmotionSummary - single record
        emotion_summary = EmotionSummary(
            analysis_id=analysis.id,
            emotion_percentages=sentiment_summary.get('emotion_percentages', {}),
            emotion_counts=sentiment_summary.get('emotion_counts', {}),
            primary_emotion_counts=sentiment_summary.get('primary_emotion_counts', {})
        )
        db.session.add(emotion_summary)
        app.logger.info(f"Created EmotionSummary")
        
        # 3. BULK INSERT TimelineSegments using constants
        detailed_analyses = sentiment_data.get('detailed_analyses', [])
        timeline_segments_data = []
        
        for idx, segment in enumerate(detailed_analyses):
            primary_emotion = segment.get('primary_emotion', segment.get('emotion', 'neutral'))
            dialogue_emotions_raw = segment.get('dialogue_emotions', {})
            sentiment_data_raw = segment.get('sentiment', {})
            
            # Handle dialogue_emotions being either dict or list
            if isinstance(dialogue_emotions_raw, list):
                emotion_vector = {}
                for item in dialogue_emotions_raw:
                    if isinstance(item, list) and len(item) == 2:
                        emotion_vector[item[0]] = item[1]
            elif isinstance(dialogue_emotions_raw, dict):
                emotion_vector = dialogue_emotions_raw
            else:
                emotion_vector = {}
            
            # Extract sentiment label and score
            if isinstance(sentiment_data_raw, dict):
                sentiment_label = sentiment_data_raw.get('label', 'neutral')
                sentiment_score = sentiment_data_raw.get('score', 0.0)
            else:
                sentiment_label = str(sentiment_data_raw) if sentiment_data_raw else 'neutral'
                sentiment_score = 0.0
            
            confidence = emotion_vector.get(primary_emotion, 0.5) if emotion_vector else 0.5
            
            # Build dict using constants
            timeline_segments_data.append({
                Columns.ANALYSIS_ID: analysis.id,
                Columns.SEGMENT_INDEX: idx,
                Columns.START_TIME: float(idx),
                Columns.END_TIME: float(idx + 1),
                'duration': 1.0,
                Columns.TEXT_CONTENT: segment.get('text', ''),
                Columns.PRIMARY_EMOTION: primary_emotion,
                Columns.SENTIMENT_LABEL: sentiment_label,
                Columns.SENTIMENT_SCORE: sentiment_score,
                Columns.CONFIDENCE_SCORE: confidence,
                Columns.EMOTION_VECTOR: emotion_vector if emotion_vector else None
            })
        
        # Bulk insert all segments at once
        if timeline_segments_data:
            db.session.bulk_insert_mappings(TimelineSegment, timeline_segments_data)
            app.logger.info(f"Bulk inserted {len(timeline_segments_data)} TimelineSegments")
        
        # 4. BULK INSERT ChartBins using constants
        if has_chart and 'timeline' in chart_data:
            timeline_bins = chart_data['timeline'].get('timeline_bins', [])
            chart_bins_data = []
            
            for bin_data in timeline_bins:
                chart_bins_data.append({
                    Columns.ANALYSIS_ID: analysis.id,
                    Columns.BIN_INDEX: bin_data.get('bin_index', 0),
                    Columns.START_TIME: bin_data.get('start_time', 0.0),
                    Columns.END_TIME: bin_data.get('end_time', 0.0),
                    Columns.FORMATTED_START: bin_data.get('formatted_start', ''),
                    Columns.FORMATTED_END: bin_data.get('formatted_end', ''),
                    Columns.DOMINANT_EMOTION: bin_data.get('dominant_emotion', 'neutral'),
                    Columns.EMOTION_COUNTS: bin_data.get('emotion_counts', {}),
                    Columns.EMOTION_PERCENTAGES: bin_data.get('emotion_percentages', {})
                })
            
            if chart_bins_data:
                db.session.bulk_insert_mappings(ChartBin, chart_bins_data)
                app.logger.info(f"Bulk inserted {len(chart_bins_data)} ChartBins")
        
        # 5. Create TranscriptSummary - single record
        if has_summary:
            transcript_sum = TranscriptSummary(
                analysis_id=analysis.id,
                content=summary_data.get('final_summary_preview', ''),
                length_profile=summary_data.get('length_profile', 'medium'),
                num_segments=summary_data.get('num_segments', 0)
            )
            db.session.add(transcript_sum)
            app.logger.info(f"Created TranscriptSummary")
        
        # 6. BULK INSERT Keywords using constants
        if has_keywords:
            keyword_list = keyword_data.get('keywords', [])
            keywords_data = []
            
            for idx, kw in enumerate(keyword_list[:50]):
                keywords_data.append({
                    Columns.ANALYSIS_ID: analysis.id,
                    Columns.TEXT: kw.get('text', ''),
                    Columns.RANK: idx + 1,
                    Columns.VALUE: kw.get('value', 0),
                    Columns.TF_IDF: kw.get('tf_idf_score', 0.0),
                    Columns.RELEVANCE_SCORE: kw.get('relevance_score', 0.0)
                })
            
            if keywords_data:
                db.session.bulk_insert_mappings(Keyword, keywords_data)
                app.logger.info(f"Bulk inserted {len(keywords_data)} Keywords")
        
        # 7. BULK INSERT TopicSentiments using constants
        if has_insights and 'topics' in insights_data:
            topics = insights_data.get('topics', [])[:10]
            topics_data = []
            
            for topic_item in topics:
                if isinstance(topic_item, list) and len(topic_item) >= 2:
                    topics_data.append({
                        Columns.ANALYSIS_ID: analysis.id,
                        Columns.TOPIC_NAME: topic_item[0],
                        Columns.TOTAL_SEGMENTS: topic_item[1],
                        Columns.DOMINANT_EMOTION: 'neutral',
                        Columns.AVERAGE_CONFIDENCE: 0.0,
                        Columns.EMOTION_DIVERSITY: 0.0,
                        Columns.TIME_SPAN_SECONDS: 0.0
                    })
            
            if topics_data:
                db.session.bulk_insert_mappings(TopicSentiment, topics_data)
                app.logger.info(f"Bulk inserted {len(topics_data)} TopicSentiments")
        
        # 8. BULK INSERT DetectedQuestions using constants
        if has_insights:
            sentiment_sum = insights_data.get('sentiment_summary', {})
            questions_detected = sentiment_sum.get('questions_detected', {})
            questions_list = questions_detected.get('questions_by_time', [])
            questions_data = []
            
            for q in questions_list[:20]:
                if isinstance(q, dict):
                    questions_data.append({
                        Columns.ANALYSIS_ID: analysis.id,
                        Columns.QUESTION_TEXT: q.get('question_text', ''),
                        Columns.PATTERN_MATCHED: q.get('pattern_matched', ''),
                        Columns.POSITION_INDEX: q.get('position', 0),
                        Columns.CONFIDENCE: q.get('confidence', 0.0)
                    })
            
            if questions_data:
                db.session.bulk_insert_mappings(DetectedQuestion, questions_data)
                app.logger.info(f"Bulk inserted {len(questions_data)} DetectedQuestions")
        
        # 9. BULK INSERT DetectedActions using constants
        if has_insights:
            actions_detected = sentiment_sum.get('action_items_detected', {})
            actions_list = actions_detected.get('actions_by_time', [])
            actions_data = []
            
            for a in actions_list[:20]:
                if isinstance(a, dict):
                    actions_data.append({
                        Columns.ANALYSIS_ID: analysis.id,
                        Columns.ACTION_TEXT: a.get('action_text', ''),
                        Columns.PATTERN_MATCHED: a.get('pattern_matched', ''),
                        Columns.POSITION_INDEX: a.get('position', 0),
                        Columns.CONFIDENCE: a.get('confidence', 0.0)
                    })
            
            if actions_data:
                db.session.bulk_insert_mappings(DetectedAction, actions_data)
                app.logger.info(f"Bulk inserted {len(actions_data)} DetectedActions")
        
        # 10. Create TextInsight - single record
        if has_insights:
            text_stats = insights_data.get('text_statistics', {})
            
            text_insight = TextInsight(
                analysis_id=analysis.id,
                top_bigrams=insights_data.get('top_bigrams', []),
                top_trigrams=insights_data.get('top_trigrams', []),
                important_sentences=insights_data.get('important_sentences', []),
                avg_sentence_length=text_stats.get('avg_sentence_length_tokens', 0.0),
                avg_word_length=text_stats.get('avg_word_length', 0.0)
            )
            db.session.add(text_insight)
            app.logger.info(f"Created TextInsight")
        
        # Single commit at the end
        db.session.commit()
        app.logger.info(f"✓ NlpAnalysis ID: {analysis.id} successfully added")
        app.logger.info(f"✓ Linked to Experiment: '{experiment.title}' (ID: {experiment.id})")
        
        return analysis.id
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error inserting analysis data: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return None