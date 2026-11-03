import streamlit as st
from chatbot import get_bot_response

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Feedback Assistant",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# 2. PAGE TITLE
# ==========================================

st.title("🤖 AI Feedback Assistant")

st.write(
    "Your personal assistant to understand feedback "
    "analysis, sentiment scores, and feedback quality."
)

st.divider()

# ==========================================
# 3. CHATBOT WELCOME MESSAGE
# ==========================================

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 Welcome to your Feedback Assistant.\n\n"
                "I can help you understand:\n"
                "- Feedback quality scores\n"
                "- Positive, negative, and neutral sentiment\n"
                "- Ways to improve your feedback\n"
                "- Your latest feedback analysis\n\n"
                "How can I help you today?"
            )
        }
    ]

# ==========================================
# 4. DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.chat_messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

# ==========================================
# 5. CHAT INPUT
# ==========================================

user_question = st.chat_input(
    "Ask your question here..."
)

if user_question:

    # Display user message
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):
        st.write(user_question)

    # Generate chatbot response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = get_bot_response(
                user_question,
                st.session_state.latest_result
            )

            st.write(response)

    # Save assistant response
    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

# ==========================================
# 6. CLEAR CHAT
# ==========================================

st.divider()

if st.button("🗑️ Clear Chat History"):

    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 Welcome back to your "
                "Feedback Assistant. How can I help you?"
            )
        }
    ]

    st.rerun()

# ==========================================
# 7. FOOTER
# ==========================================

st.divider()

st.caption(
    "AI Feedback Assistant | Powered by Python and Streamlit"
)