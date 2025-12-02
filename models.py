from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))

    def __repr__(self):
        return f"<Name {self.first_name} {self.last_name}>"

class Experiment(db.Model):
    """
    Represents a manual experiment entry created by a user.
    """
    __tablename__ = "experiments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(200))
    participant_count = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)
    avg_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(150), default="Completed")

    # Relationship to analysis
    analysis = db.relationship('NlpAnalysis', backref='experiment', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Experiment {self.title}>"
    
    def format_duration(self):
        if self.duration is None:
            return "N/A"
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}min"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}min"

class NlpAnalysis(db.Model):
    """
    The root table for all automated analysis data coming from MinIO.
    """
    __tablename__ = 'nlp_analysis'

    id = db.Column(db.Integer, primary_key=True)
    # Links automated analysis to a manual experiment entry
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=True)
    
    # Metadata from source files
    source_filename = db.Column(db.String(255)) # e.g. "3x_ptz_cameras_part_2_video1"
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed_at = db.Column(db.DateTime) # From sentiment.json "analyzed_at"
    model_used = db.Column(db.String(100)) # From sentiment.json "model_used"
    
    # High-level statistics from insights.json
    total_segments = db.Column(db.Integer)
    reading_time_minutes = db.Column(db.Float)
    word_count = db.Column(db.Integer)
    unique_words_count = db.Column(db.Integer)
    lexical_diversity = db.Column(db.Float)
    dominant_emotion = db.Column(db.String(50))

    # Relationships to detailed data
    emotion_summary = db.relationship('EmotionSummary', backref='analysis', uselist=False, cascade='all, delete-orphan')
    transcript_summary = db.relationship('TranscriptSummary', backref='analysis', uselist=False, cascade='all, delete-orphan')
    timeline_segments = db.relationship('TimelineSegment', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    keywords = db.relationship('Keyword', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    topics = db.relationship('TopicSentiment', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    questions = db.relationship('DetectedQuestion', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    actions = db.relationship('DetectedAction', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    chart_bins = db.relationship('ChartBin', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    text_insights = db.relationship('TextInsight', backref='analysis', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<NlpAnalysis {self.id} - {self.source_filename}>"

class EmotionSummary(db.Model):
    """
    Aggregated emotion statistics.
    Source: sentiment.json and insights.json
    """
    __tablename__ = 'emotion_summary'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)

    emotion_percentages = db.Column(JSONB) 
    emotion_counts = db.Column(JSONB)
    primary_emotion_counts = db.Column(JSONB)
    
    # Transition matrix for emotion flow (from sentiment.json)
    emotion_transitions = db.Column(JSONB)
    stability_score = db.Column(db.Float)

class TimelineSegment(db.Model):
    """
    Sentence-by-sentence analysis.
    Source: sentiment.json -> detailed_analyses
    """
    __tablename__ = 'timeline_segments'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    segment_index = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    duration = db.Column(db.Float)
    
    text_content = db.Column(db.Text)
    
    # Sentiment specific
    primary_emotion = db.Column(db.String(50)) 
    sentiment_label = db.Column(db.String(50)) # positive/negative/neutral
    sentiment_score = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    
    # Stores the full vector object: {"neutral": 0.75, "happy": 0.23, "sad": 0.01}
    emotion_vector = db.Column(JSONB) 

class ChartBin(db.Model):
    """
    Pre-aggregated time bins (e.g., every 60 seconds) for faster UI charting.
    Source: chart_data.json -> timeline_bins
    """
    __tablename__ = 'chart_bins'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    bin_index = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    formatted_start = db.Column(db.String(20)) # "00:00:00"
    formatted_end = db.Column(db.String(20))
    
    dominant_emotion = db.Column(db.String(50))
    # Aggregated counts for this specific bin
    emotion_counts = db.Column(JSONB) 
    emotion_percentages = db.Column(JSONB)

class TranscriptSummary(db.Model):
    """
    AI-generated text summary.
    Source: summary.json
    """
    __tablename__ = 'transcript_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    content = db.Column(db.Text) # "final_summary_preview"
    length_profile = db.Column(db.String(50)) # "medium"
    num_segments = db.Column(db.Integer)

class Keyword(db.Model):
    """
    Word cloud data.
    Source: keyword_cloud.json
    """
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    text = db.Column(db.String(100))
    rank = db.Column(db.Integer)
    value = db.Column(db.Integer) # Count
    tf_idf_score = db.Column(db.Float)
    relevance_score = db.Column(db.Float)

class TopicSentiment(db.Model):
    """
    Sentiment analysis grouped by topic (e.g., "Technology", "Meeting").
    Source: sentiment.json -> topic_sentiment
    """
    __tablename__ = 'topic_sentiments'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    topic_name = db.Column(db.String(100)) 
    total_segments = db.Column(db.Integer)
    dominant_emotion = db.Column(db.String(50))
    average_confidence = db.Column(db.Float)
    emotion_diversity = db.Column(db.Float)
    time_span_seconds = db.Column(db.Float)
    
    # Store sample segments text as JSON list
    sample_segments = db.Column(JSONB) 

class DetectedQuestion(db.Model):
    """
    Questions detected in the transcript.
    Source: insights.json -> questions_detected
    """
    __tablename__ = 'detected_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    question_text = db.Column(db.Text)
    pattern_matched = db.Column(db.String(255))
    position_index = db.Column(db.Integer) # position in text
    confidence = db.Column(db.Float)

class DetectedAction(db.Model):
    """
    Action items detected in the transcript.
    Source: insights.json -> action_items_detected
    """
    __tablename__ = 'detected_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    action_text = db.Column(db.Text)
    pattern_matched = db.Column(db.String(255))
    position_index = db.Column(db.Integer)
    confidence = db.Column(db.Float)

class TextInsight(db.Model):
    """
    Linguistic insights like bigrams and important sentences.
    Source: insights.json
    """
    __tablename__ = 'text_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('nlp_analysis.id'), nullable=False)
    
    # Storing lists of strings/arrays as JSONB
    top_bigrams = db.Column(JSONB) 
    top_trigrams = db.Column(JSONB)
    important_sentences = db.Column(JSONB)
    
    avg_sentence_length = db.Column(db.Float)
    avg_word_length = db.Column(db.Float)