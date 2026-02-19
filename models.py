from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON
from db_names import Tables, Columns

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = Tables.USERS

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))

    def __repr__(self):
        return f"<Name {self.first_name} {self.last_name}>"


class Experiment(db.Model):
    __tablename__ = Tables.EXPERIMENTS

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True)
    
    # Manual entry field
    description = db.Column(db.Text)
    
    date = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(200))
    participant_count = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    status = db.Column(db.String(150), default="Completed")

    # Add fields to mirror key analysis data for easier access
    has_transcription = db.Column(db.Boolean, default=False)
    has_tracking = db.Column(db.Boolean, default=False)
    dominant_emotion = db.Column(db.String(50))
    word_count = db.Column(db.Integer)

    # Relationship to analysis
    nlp_analysis = db.relationship(
        "NlpAnalysis",
        backref="experiment",
        uselist=False,
        cascade="all, delete-orphan"
    )
    tracking_analysis = db.relationship(
        "TrackingAnalysis",
        backref="experiment",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Experiment {self.title}>"

    def format_duration(self):
        # First try to use the stored duration
        total_sec = self.duration_seconds if self.duration_seconds is not None else (self.duration * 60 if self.duration else None)
    
        if total_sec is None:
            return "N/A"

        # Calculate time units
        hours, remainder = divmod(total_sec, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Build string based on what data exists
        parts = []
        if hours > 0:
            parts.append(f"{int(hours)}h")
        if minutes > 0:
            parts.append(f"{int(minutes)}m")
        if seconds > 0 or not parts:
            parts.append(f"{int(seconds)}s")

        return " ".join(parts)
    
    @property
    def calculated_duration(self):
        if self.nlp_analysis and self.nlp_analysis.timeline_segments.count() > 0:
            segments = self.nlp_analysis.timeline_segments.all()
            if segments:
                total_duration = max(seg.end_time for seg in segments)
                return int(total_duration / 60)
        return None

    @property
    def effective_description(self):
        """
        Smart property for templates.
        Returns the manual description if it exists.
        If not, dynamically fetches the AI transcript summary.
        """
        # 1. Return manual description if present
        if self.description and self.description.strip():
            return self.description
        
        # 2. Fallback to AI Transcript Summary
        if self.nlp_analysis and self.nlp_analysis.transcript_summary:
            return self.nlp_analysis.transcript_summary.summary
        
        return None

    def sync_from_analysis(self):
        """Sync key fields from analysis tables to experiment for quick access"""
        if self.nlp_analysis:
            self.has_transcription = True
            self.dominant_emotion = self.nlp_analysis.dominant_emotion
            self.word_count = self.nlp_analysis.word_count
            
            # If manual description is empty, auto-fill it with AI summary
            if not self.description and self.nlp_analysis.transcript_summary:
                self.description = self.nlp_analysis.transcript_summary.summary
        
        if self.tracking_analysis:
            self.has_tracking = True
    
    @property
    def has_transcription_data(self):
        """Check if experiment has NLP/transcription data"""
        return self.nlp_analysis is not None
    
    @property
    def has_tracking_data(self):
        """Check if experiment has CV/tracking data"""
        return (self.tracking_analysis is not None and 
                self.tracking_analysis.detections is not None)
    
    @property
    def has_emotion_data(self):
        """Check if experiment has emotion analysis"""
        return (self.nlp_analysis is not None and 
                self.nlp_analysis.emotion_data is not None)


class TrackingAnalysis(db.Model):
    """Computer Vision / Detection data"""
    __tablename__ = Tables.TRACKING_ANALYSIS

    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.EXPERIMENTS}.id"),
        nullable=True,
    )
    
    source_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    detections = db.Column(JSON)

    def __repr__(self):
        return f"<TrackingAnalysis {self.id} for Exp {self.experiment_id}>"
    
    @property
    def total_people(self):
        """Count unique people detected"""
        if not self.detections or 'people' not in self.detections:
            return 0
        return len(self.detections['people'])
    
    @property
    def total_visits(self):
        """Count total visits across all people"""
        if not self.detections or 'people' not in self.detections:
            return 0
        return sum(len(p.get('visits', [])) for p in self.detections['people'])
    
    @property
    def camera_distribution(self):
        """Get visit count per camera"""
        dist = {'CAM_01': 0, 'CAM_02': 0, 'CAM_03': 0, 'CAM_04': 0}
        
        if not self.detections or 'people' not in self.detections:
            return dist
        
        for person in self.detections['people']:
            for visit in person.get('visits', []):
                cam = visit.get('camera_id')
                if cam in dist:
                    dist[cam] += 1
        
        return dist
    
    @property
    def avg_confidence(self):
        """Calculate average detection confidence"""
        if not self.detections or 'people' not in self.detections:
            return 0.0
        
        confidences = []
        for person in self.detections['people']:
            for visit in person.get('visits', []):
                confidences.append(visit.get('avg_confidence', 0.5))
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    @property
    def timeline_data(self):
        """Get processed timeline if available"""
        if self.detections and 'processed_timeline' in self.detections:
            return self.detections['processed_timeline']
        return []
    
    @property
    def transitions(self):
        """Get movement transitions if available"""
        if self.detections and 'transitions' in self.detections:
            return self.detections['transitions']
        return {}


class NlpAnalysis(db.Model):
    __tablename__ = Tables.NLP_ANALYSIS

    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.EXPERIMENTS}.id"),
        nullable=True,
    )

    # Metadata from source files
    source_filename = db.Column(db.String(255))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed_at = db.Column(db.DateTime)
    model_used = db.Column(db.String(100))

    # High-level statistics from insights.json
    total_segments = db.Column(db.Integer)
    reading_time_minutes = db.Column(db.Float)
    word_count = db.Column(db.Integer)
    unique_words_count = db.Column(db.Integer)
    lexical_diversity = db.Column(db.Float)
    dominant_emotion = db.Column(db.String(50))

    # Relationships to detailed data
    emotion_data = db.relationship(
        "EmotionData", 
        backref="nlp_analysis", 
        uselist=False, 
        cascade="all, delete-orphan"
    )
    transcript_summary = db.relationship(
        "TranscriptSummary", 
        backref="nlp_analysis", 
        uselist=False, 
        cascade="all, delete-orphan"
    )
    timeline_segments = db.relationship(
        "TimelineSegment", 
        backref="nlp_analysis", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    keywords = db.relationship(
        "Keyword", 
        backref="nlp_analysis", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    topics = db.relationship(
        "TopicSentiment", 
        backref="nlp_analysis", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    questions = db.relationship(
        "DetectedQuestion", 
        backref="nlp_analysis", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    actions = db.relationship(
        "DetectedAction", 
        backref="nlp_analysis", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    chart_bins = db.relationship(
        "ChartBin", 
        backref="nlp_analysis", 
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )
    text_insights = db.relationship(
        "TextInsight", 
        backref="nlp_analysis", 
        uselist=False, 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<NlpAnalysis {self.id} - {self.source_filename}>"


class EmotionData(db.Model):
    __tablename__ = Tables.EMOTION_DATA

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    emotion_percentages = db.Column(JSON)
    emotion_counts = db.Column(JSON)
    primary_emotion_counts = db.Column(JSON)
    emotion_transitions = db.Column(JSON)
    stability_score = db.Column(db.Float)


class TimelineSegment(db.Model):
    __tablename__ = Tables.TIMELINE_SEGMENTS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    segment_index = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    duration = db.Column(db.Float)

    text_content = db.Column(db.Text)
    primary_emotion = db.Column(db.String(50))
    sentiment_label = db.Column(db.String(50))
    sentiment_score = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    emotion_vector = db.Column(JSON)


class ChartBin(db.Model):
    __tablename__ = Tables.CHART_BINS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    bin_index = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    formatted_start = db.Column(db.String(20))
    formatted_end = db.Column(db.String(20))

    dominant_emotion = db.Column(db.String(50))
    emotion_counts = db.Column(JSON)
    emotion_percentages = db.Column(JSON)


class TranscriptSummary(db.Model):
    __tablename__ = Tables.TRANSCRIPT_SUMMARY

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    summary = db.Column(db.Text)
    length_profile = db.Column(db.String(50))
    num_segments = db.Column(db.Integer)


class Keyword(db.Model):
    __tablename__ = Tables.KEYWORDS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    text = db.Column(db.String(100))
    rank = db.Column(db.Integer)
    value = db.Column(db.Integer)
    tf_idf_score = db.Column(db.Float)
    relevance_score = db.Column(db.Float)


class TopicSentiment(db.Model):
    __tablename__ = Tables.TOPIC_SENTIMENTS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    topic_name = db.Column(db.String(100))
    total_segments = db.Column(db.Integer)
    dominant_emotion = db.Column(db.String(50))
    average_confidence = db.Column(db.Float)
    emotion_diversity = db.Column(db.Float)
    time_span_seconds = db.Column(db.Float)
    sample_segments = db.Column(JSON)


class DetectedQuestion(db.Model):
    __tablename__ = Tables.DETECTED_QUESTIONS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    question_text = db.Column(db.Text)
    pattern_matched = db.Column(db.String(255))
    position_index = db.Column(db.Integer)
    confidence = db.Column(db.Float)


class DetectedAction(db.Model):
    __tablename__ = Tables.DETECTED_ACTIONS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    action_text = db.Column(db.Text)
    pattern_matched = db.Column(db.String(255))
    position_index = db.Column(db.Integer)
    confidence = db.Column(db.Float)


class TextInsight(db.Model):
    __tablename__ = Tables.TEXT_INSIGHTS

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{Tables.NLP_ANALYSIS}.id"),
        nullable=False,
    )

    top_bigrams = db.Column(JSON)
    top_trigrams = db.Column(JSON)
    important_sentences = db.Column(JSON)

    avg_sentence_length = db.Column(db.Float)
    avg_word_length = db.Column(db.Float)

    action_items = db.Column(JSON)
    multi_emotion_segments = db.Column(JSON)