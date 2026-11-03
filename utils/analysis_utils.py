
import re
import nltk

from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS


# ==================================================
# INITIALIZE SENTIMENT ANALYZER
# ==================================================

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    try:
        nltk.data.find("sentiment/vader_lexicon")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)

sia = SentimentIntensityAnalyzer()


# ==================================================
# 1. SENTIMENT ANALYSIS
# ==================================================

def analyze_sentiment(feedback):

    scores = sia.polarity_scores(str(feedback))

    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "Positive"

    elif compound <= -0.05:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return sentiment, compound


# ==================================================
# 2. CATEGORY CLASSIFICATION
# ==================================================

def classify_feedback_category(feedback):

    feedback = str(feedback).lower()

    categories = {

        "Teaching": [
            "teacher", "teaching", "trainer",
            "explanation", "lecture", "instructor"
        ],

        "Course Content": [
            "course", "syllabus", "content",
            "topic", "subject", "curriculum"
        ],

        "Practical Sessions": [
            "practical", "hands-on", "project",
            "lab", "practice", "coding"
        ],

        "Infrastructure": [
            "classroom", "computer", "internet",
            "wifi", "facilities", "infrastructure"
        ],

        "Time Management": [
            "time", "schedule", "duration",
            "break", "timing", "late"
        ]
    }

    for category, keywords in categories.items():

        if any(word in feedback for word in keywords):
            return category

    return "Other"


# ==================================================
# 3. QUALITY EVALUATION
# ==================================================

def evaluate_quality(feedback):

    feedback = str(feedback).strip()

    text = feedback.lower()

    # Length score (30)
    if len(feedback) >= 100:
        length_score = 30

    elif len(feedback) >= 50:
        length_score = 20

    elif len(feedback) >= 20:
        length_score = 10

    else:
        length_score = 0

    # Specific details score (30)
    details = [
        "because", "example", "session",
        "topic", "trainer", "course",
        "project", "practical", "training"
    ]

    detail_count = sum(
        1 for word in details if word in text
    )

    if detail_count >= 3:
        detail_score = 30

    elif detail_count >= 1:
        detail_score = 15

    else:
        detail_score = 0

    # Actionable suggestions score (25)
    suggestions = [
        "should", "could", "improve",
        "suggest", "more", "less",
        "need", "better", "recommend"
    ]

    suggestion_count = sum(
        1 for word in suggestions if word in text
    )

    if suggestion_count >= 2:
        suggestion_score = 25

    elif suggestion_count >= 1:
        suggestion_score = 15

    else:
        suggestion_score = 0

    # Clarity score (15)
    word_count = len(feedback.split())

    if word_count >= 15:
        clarity_score = 15

    elif word_count >= 5:
        clarity_score = 10

    else:
        clarity_score = 0

    # Breakdown
    breakdown = {

        "Length": length_score,

        "Specific Details": detail_score,

        "Actionable Suggestions": suggestion_score,

        "Clarity": clarity_score
    }

    # Total score
    quality_score = sum(breakdown.values())

    # Quality label
    if quality_score >= 70:
        quality_label = "High"

    elif quality_score >= 40:
        quality_label = "Moderate"

    else:
        quality_label = "Low"

    return quality_score, quality_label, breakdown


# ==================================================
# 4. IMPROVEMENT SUGGESTIONS
# ==================================================

def generate_suggestions(feedback, quality_score, breakdown):

    suggestions = []

    if breakdown["Length"] < 30:

        suggestions.append(
            "Provide more details to make your feedback meaningful."
        )

    if breakdown["Specific Details"] < 30:

        suggestions.append(
            "Include specific examples or experiences."
        )

    if breakdown["Actionable Suggestions"] < 25:

        suggestions.append(
            "Add practical suggestions describing what could be improved."
        )

    if breakdown["Clarity"] < 15:

        suggestions.append(
            "Write complete sentences and explain your thoughts clearly."
        )

    if quality_score >= 70:

        suggestions.append(
            "Excellent! Your feedback is detailed and useful."
        )

    if not suggestions:

        suggestions.append(
            "Your feedback is good. Keep sharing meaningful opinions."
        )

    return suggestions


# ==================================================
# 5. WORD CLOUD GENERATION
# ==================================================

def generate_wordcloud(feedback):

    feedback = str(feedback).lower()

    feedback = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        feedback
    )

    stopwords = STOPWORDS.union({

        "good", "bad", "very", "also",
        "much", "many", "really", "would",
        "could", "should", "like", "one"

    })

    wordcloud = WordCloud(

        width=1000,

        height=500,

        background_color="white",

        colormap="viridis",

        max_words=100,

        stopwords=stopwords,

        collocations=False

    ).generate(feedback)

    return wordcloud


# ==================================================
# BACKWARD COMPATIBILITY
# ==================================================

def calculate_quality_score(feedback):

    score, label, breakdown = evaluate_quality(feedback)

    return score


def get_quality_label(score):

    if score >= 70:
        return "High" 

    elif score >= 40:
        return "Moderate"

    else:
        return "Low"