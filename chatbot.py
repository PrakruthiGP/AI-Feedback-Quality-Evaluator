# ==========================================
# AI FEEDBACK ASSISTANT - CHATBOT BACKEND
# ==========================================

def get_bot_response(user_question, latest_result=None):

    question = user_question.lower().strip()

    # Greeting responses
    if any(word in question for word in ["hello", "hi", "hey"]):
        return (
            "Hello! 👋 Welcome to your AI Feedback Assistant.\n\n"
            "I can help you understand feedback quality, "
            "sentiment analysis, scores, and suggestions. "
            "What would you like to know?"
        )

    # Quality score explanation
    elif "quality score" in question or "quality" in question:
        return (
            "📊 Feedback Quality Score\n\n"
            "Your feedback quality score is calculated "
            "out of 100 using four factors:\n\n"
            "1. Length (30 marks): Checks the amount of detail.\n"
            "2. Specific Details (30 marks): Checks whether "
            "you mention topics, trainers, sessions, etc.\n"
            "3. Actionable Suggestions (25 marks): Checks "
            "whether you provide suggestions for improvement.\n"
            "4. Clarity (15 marks): Checks the basic length "
            "requirement for understandable feedback.\n\n"
            "A higher score indicates more useful and detailed "
            "feedback according to the predefined rules."
        )

    # Sentiment explanation
    elif "sentiment" in question:
        return (
            "😊 Sentiment Analysis\n\n"
            "This project uses NLTK VADER to identify "
            "the emotional tone of written feedback.\n\n"
            "Positive: Compound score >= 0.05\n"
            "Negative: Compound score <= -0.05\n"
            "Neutral: Compound score between -0.05 and 0.05.\n\n"
            "The compound score ranges from -1 to +1."
        )

    # Latest result
    elif any(word in question for word in [
        "my result", "latest result", "my analysis",
        "my score", "analyzed feedback"
    ]):
        if latest_result is None:
            return (
                "You haven't analyzed any feedback yet. "
                "Please visit the Feedback Analysis page "
                "and submit your feedback first. 😊"
            )

        return (
            "📋 Your Latest Feedback Analysis\n\n"
            f"Sentiment: {latest_result['sentiment']}\n\n"
            f"Quality Score: {latest_result['quality_score']}/100\n\n"
            f"Quality Level: {latest_result['quality_label']}\n\n"
            f"VADER Compound Score: "
            f"{latest_result['compound_score']:.3f}\n\n"
            "Would you like me to explain any of these results?"
        )

    # Improving feedback
    elif any(word in question for word in [
        "improve", "better", "suggestion",
        "suggestions", "increase", "improvement"
    ]):
        return (
            "💡 Tips to Improve Feedback Quality\n\n"
            "1. Write at least 15 meaningful words.\n"
            "2. Mention specific details about the trainer, "
            "course, session, or project.\n"
            "3. Include practical examples from your experience.\n"
            "4. Suggest improvements wherever necessary.\n"
            "5. Use clear and understandable sentences.\n\n"
            "Remember: Detailed and constructive feedback "
            "is more useful than very short comments."
        )

    # Rating explanation
    elif "rating" in question or "star" in question:
        return (
            "⭐ Rating Information\n\n"
            "You can rate your experience from 1 to 5 stars.\n\n"
            "1 = Very Poor\n"
            "2 = Poor\n"
            "3 = Average\n"
            "4 = Good\n"
            "5 = Excellent\n\n"
            "The rating is displayed separately from the "
            "feedback quality score."
        )

    # Project explanation
    elif any(word in question for word in [
        "project", "objective", "methodology", "technology",
        "technologies", "how does", "working"
    ]):
        return (
            "📊 About the AI Feedback Quality Evaluator\n\n"
            "This project analyzes written feedback to "
            "understand its sentiment and estimate its quality.\n\n"
            "Technologies used:\n"
            "- Python\n"
            "- Streamlit\n"
            "- Pandas\n"
            "- NLTK VADER\n"
            "- Matplotlib\n\n"
            "Sentiment is analyzed using VADER, while feedback "
            "quality is evaluated using predefined rules. "
            "The current version does not train a machine-learning "
            "model."
        )

    # Help response
    elif any(word in question for word in [
        "help", "what can you do", "features"
    ]):
        return (
            "🤖 I'm your AI Feedback Assistant!\n\n"
            "You can ask me questions about:\n\n"
            "- Feedback quality scores\n"
            "- Sentiment analysis\n"
            "- Latest feedback results\n"
            "- Improving feedback quality\n"
            "- Rating system\n"
            "- Project methodology and technologies\n\n"
            "Type your question and I'll help you!"
        )

    # Default response
    else:
        return (
            "I'm here to help you with your Feedback Quality "
            "Evaluator! 😊\n\n"
            "Try asking me:\n"
            "- What is a quality score?\n"
            "- Explain sentiment analysis.\n"
            "- How can I improve my feedback?\n"
            "- Show my latest result.\n"
            "- Explain this project.\n\n"
            "I'll do my best to guide you!"
        )