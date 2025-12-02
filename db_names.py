class Tables:
    USERS = "users"
    EXPERIMENTS = "experiments"
    NLP_ANALYSIS = "nlp_analysis"
    EMOTION_SUMMARY = "emotion_summary"
    TIMELINE_SEGMENTS = "timeline_segments"
    CHART_BINS = "chart_bins"
    TRANSCRIPT_SUMMARIES = "transcript_summaries"
    KEYWORDS = "keywords"
    TOPIC_SENTIMENTS = "topic_sentiments"
    DETECTED_QUESTIONS = "detected_questions"
    DETECTED_ACTIONS = "detected_actions"
    TEXT_INSIGHTS = "text_insights"


class Columns:
    # shared
    ID = "id"
    ANALYSIS_ID = "analysis_id"
    EXPERIMENT_ID = "experiment_id"
    CREATED_AT = "created_at"

    # user
    EMAIL = "email"
    PASSWORD = "password"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"

    # experiment
    TITLE = "title"
    DESCRIPTION = "description"
    DATE = "date"
    TAGS = "tags"
    PARTICIPANT_COUNT = "participant_count"
    DURATION = "duration"
    AVG_SCORE = "avg_score"
    STATUS = "status"

    # nlp analysis
    SOURCE_FILENAME = "source_filename"
    GENERATED_AT = "generated_at"
    ANALYZED_AT = "analyzed_at"
    MODEL_USED = "model_used"
    TOTAL_SEGMENTS = "total_segments"
    READING_TIME_MINUTES = "reading_time_minutes"
    WORD_COUNT = "word_count"
    UNIQUE_WORDS_COUNT = "unique_words_count"
    LEXICAL_DIVERSITY = "lexical_diversity"
    DOMINANT_EMOTION = "dominant_emotion"

    # emotion summary
    EMOTION_PERCENTAGES = "emotion_percentages"
    EMOTION_COUNTS = "emotion_counts"
    PRIMARY_EMOTION_COUNTS = "primary_emotion_counts"
    EMOTION_TRANSITIONS = "emotion_transitions"
    STABILITY_SCORE = "stability_score"

    # timeline segment
    SEGMENT_INDEX = "segment_index"
    START_TIME = "start_time"
    END_TIME = "end_time"
    SEGMENT_DURATION = "segment_duration"
    TEXT_CONTENT = "text_content"
    PRIMARY_EMOTION = "primary_emotion"
    SENTIMENT_LABEL = "sentiment_label"
    SENTIMENT_SCORE = "sentiment_score"
    CONFIDENCE_SCORE = "confidence_score"
    EMOTION_VECTOR = "emotion_vector"

    # chart bins
    BIN_INDEX = "bin_index"
    FORMATTED_START = "formatted_start"
    FORMATTED_END = "formatted_end"

    # transcript summary
    CONTENT = "content"
    LENGTH_PROFILE = "length_profile"
    NUM_SEGMENTS = "num_segments"

    # keyword
    TEXT = "text"
    RANK = "rank"
    VALUE = "value"
    TF_IDF = "tf_idf_score"
    RELEVANCE_SCORE = "relevance_score"

    # topic sentiment
    TOPIC_NAME = "topic_name"
    AVERAGE_CONFIDENCE = "average_confidence"
    EMOTION_DIVERSITY = "emotion_diversity"
    TIME_SPAN_SECONDS = "time_span_seconds"
    SAMPLE_SEGMENTS = "sample_segments"

    # detected question / action
    QUESTION_TEXT = "question_text"
    ACTION_TEXT = "action_text"
    PATTERN_MATCHED = "pattern_matched"
    POSITION_INDEX = "position_index"
    CONFIDENCE = "confidence"

    # text insights
    TOP_BIGRAMS = "top_bigrams"
    TOP_TRIGRAMS = "top_trigrams"
    IMPORTANT_SENTENCES = "important_sentences"
    AVG_SENTENCE_LENGTH = "avg_sentence_length"
    AVG_WORD_LENGTH = "avg_word_length"
