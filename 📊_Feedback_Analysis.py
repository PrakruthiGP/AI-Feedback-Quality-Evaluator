
import os
from io import BytesIO
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as PDFImage
)

from utils.analysis_utils import (
    analyze_sentiment,
    classify_feedback_category,
    evaluate_quality,
    generate_suggestions,
    generate_wordcloud
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Feedback Quality Evaluator",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# FILE CONFIGURATION
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "feedback_history.csv")

COLUMNS = [
    "Date & Time",
    "Feedback",
    "Rating",
    "Sentiment",
    "Compound Score",
    "Quality Score",
    "Quality Label",
    "Category"
]


# ==================================================
# SESSION STATE
# ==================================================

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Dark"

if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = pd.DataFrame(columns=COLUMNS)

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None


# ==================================================
# LIGHT / DARK THEME CONFIGURATION
# ==================================================

THEMES = {

    "Dark": {
        "BG": "#0B1020",
        "SIDEBAR": "#11182B",
        "CARD": "#141D35",
        "CARD_GRADIENT": "#192443",
        "TEXT": "#E8EAF6",
        "MUTED": "#A0ADCC",
        "BORDER": "#303D65",
        "INPUT": "#151F38",
        "PURPLE": "#A78BFA",
        "PINK": "#E879F9",
        "BLUE": "#60A5FA",
        "CYAN": "#22D3EE",
        "GRID": "#344267",
        "HEADER": "#211B49",
        "HEADER_TEXT": "#F4F0FF",
        "HEADER_MUTED": "#B9B4D8",
        "VALUE": "#C5B2FF",
        "BUTTON": "#7055D9",
        "BUTTON_HOVER": "#896DF0"
    },

    "Light": {
        "BG": "#F5F7FC",
        "SIDEBAR": "#FFFFFF",
        "CARD": "#FFFFFF",
        "CARD_GRADIENT": "#F0EDFF",
        "TEXT": "#20243A",
        "MUTED": "#68718A",
        "BORDER": "#DCE1EF",
        "INPUT": "#FFFFFF",
        "PURPLE": "#7055D9",
        "PINK": "#C04BCB",
        "BLUE": "#3679CE",
        "CYAN": "#159BB0",
        "GRID": "#DCE1EF",
        "HEADER": "#EAE5FF",
        "HEADER_TEXT": "#30205E",
        "HEADER_MUTED": "#655B83",
        "VALUE": "#6545C5",
        "BUTTON": "#7055D9",
        "BUTTON_HOVER": "#896DF0"
    }
}


THEME = THEMES[st.session_state.app_theme]

APP_BG = THEME["BG"]
SIDEBAR_BG = THEME["SIDEBAR"]
CARD_BG = THEME["CARD"]
TEXT_COLOR = THEME["TEXT"]
MUTED_COLOR = THEME["MUTED"]
BORDER_COLOR = THEME["BORDER"]
INPUT_BG = THEME["INPUT"]
PURPLE = THEME["PURPLE"]
PINK = THEME["PINK"]
BLUE = THEME["BLUE"]
CYAN = THEME["CYAN"]


# ==================================================
# THEME CSS
# ==================================================

st.markdown(
    f"""
    <style>

    /* Main background */

    .stApp {{
        background: {APP_BG};
        color: {TEXT_COLOR};
    }}

    .main .block-container {{
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    [data-testid="stHeader"] {{
        background: {APP_BG};
    }}

    /* Sidebar */

    [data-testid="stSidebar"] {{
        background: {SIDEBAR_BG};
        border-right: 1px solid {BORDER_COLOR};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT_COLOR};
    }}

    /* Text */

    h1, h2, h3, h4, h5, p, label {{
        color: {TEXT_COLOR} !important;
    }}

    h1 {{
        font-size: 2.15rem !important;
        font-weight: 800 !important;
    }}

    h2 {{
        font-size: 1.45rem !important;
        font-weight: 700 !important;
    }}

    h3 {{
        font-size: 1.1rem !important;
        font-weight: 650 !important;
    }}

    [data-testid="stCaptionContainer"] {{
        color: {MUTED_COLOR} !important;
    }}

    /* KPI cards */

    [data-testid="stMetric"] {{
        background: linear-gradient(
            145deg,
            {THEME["CARD_GRADIENT"]},
            {CARD_BG}
        );
        border: 1px solid {BORDER_COLOR};
        padding: 20px 18px;
        border-radius: 16px;
        min-height: 125px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED_COLOR} !important;
        font-size: 0.85rem !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {THEME["VALUE"]} !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }}

    [data-testid="stMetricDelta"] {{
        color: {PURPLE} !important;
    }}

    /* Buttons */

    .stButton > button,
    .stDownloadButton > button {{
        background: linear-gradient(
            110deg,
            {THEME["BUTTON"]},
            #9A6BFF
        );
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 650;
        padding: 0.55rem 1rem;
        transition: 0.2s ease;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        background: linear-gradient(
            110deg,
            {THEME["BUTTON_HOVER"]},
            #B18BFF
        );
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 16px rgba(137,109,240,0.20);
    }}

    /* Input fields */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {{
        background: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 10px !important;
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: {MUTED_COLOR} !important;
    }}

    /* Select boxes */

    [data-baseweb="select"] > div {{
        background: {INPUT_BG} !important;
        border-color: {BORDER_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    [data-baseweb="popover"] {{
        background: {CARD_BG} !important;
    }}

    [role="option"] {{
        background: {CARD_BG} !important;
        color: {TEXT_COLOR} !important;
    }}

    /* Slider */

    [data-testid="stSlider"] {{
        color: {PURPLE};
    }}

    /* Tabs */

    [data-testid="stTabs"] button {{
        color: {MUTED_COLOR} !important;
        font-weight: 650;
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: {PURPLE} !important;
        border-bottom-color: {PURPLE} !important;
    }}

    /* Dataframes */

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        overflow: hidden;
    }}

    /* Expanders */

    [data-testid="stExpander"] {{
        background: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
    }}

    /* Dividers */

    hr {{
        border-color: {BORDER_COLOR} !important;
    }}

    /* Checkboxes */

    [data-testid="stCheckbox"] label {{
        color: {TEXT_COLOR} !important;
    }}

    /* Alerts */

    [data-testid="stAlert"] {{
        border-radius: 12px;
    }}

    /* Dashboard header */

    .dashboard-header {{
        background: linear-gradient(
            120deg,
            {THEME["HEADER"]},
            {CARD_BG}
        );
        border: 1px solid {BORDER_COLOR};
        padding: 25px 28px;
        border-radius: 18px;
        margin-bottom: 22px;
    }}

    .dashboard-header h2 {{
        color: {THEME["HEADER_TEXT"]} !important;
        margin: 0;
        font-size: 1.65rem !important;
    }}

    .dashboard-header p {{
        color: {THEME["HEADER_MUTED"]} !important;
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 0.92rem;
    }}

    /* Section labels */

    .section-label {{
        color: {PURPLE};
        font-size: 0.82rem;
        font-weight: 750;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
    }}

    /* Custom cards */

    .custom-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 15px;
        padding: 17px;
        margin-bottom: 12px;
    }}

    .custom-card-title {{
        color: {MUTED_COLOR};
        font-size: 0.83rem;
        font-weight: 600;
    }}

    .custom-card-value {{
        color: {THEME["VALUE"]};
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 8px;
    }}

    .custom-card-note {{
        color: {MUTED_COLOR};
        font-size: 0.75rem;
        margin-top: 5px;
    }}

    /* Footer */

    .app-footer {{
        text-align: center;
        color: {MUTED_COLOR};
        padding: 15px;
        font-size: 12px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HISTORY FUNCTIONS
# ==================================================

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=COLUMNS)

    try:

        data = pd.read_csv(HISTORY_FILE)

        for column in COLUMNS:

            if column not in data.columns:

                if column == "Category" and "Feedback" in data.columns:

                    data[column] = data["Feedback"].apply(
                        classify_feedback_category
                    )

                else:
                    data[column] = ""

        data["Category"] = data["Category"].fillna("")

        missing_category = (
            data["Category"].astype(str).str.strip() == ""
        )

        data.loc[missing_category, "Category"] = (
            data.loc[missing_category, "Feedback"]
            .apply(classify_feedback_category)
        )

        return data[COLUMNS].copy()

    except pd.errors.EmptyDataError:

        return pd.DataFrame(columns=COLUMNS)

    except Exception as error:

        st.error(f"Error loading feedback history: {error}")

        return pd.DataFrame(columns=COLUMNS)


def save_history(data):

    data[COLUMNS].to_csv(HISTORY_FILE, index=False)


# Load existing history

st.session_state.feedback_history = load_history()


# ==================================================
# MONTHLY TRENDS
# ==================================================

def prepare_monthly_trends(df):

    trend_df = df.copy()

    trend_df["Parsed Date"] = pd.to_datetime(
        trend_df["Date & Time"],
        errors="coerce"
    )

    trend_df["Quality Score"] = pd.to_numeric(
        trend_df["Quality Score"],
        errors="coerce"
    )

    trend_df = trend_df.dropna(subset=["Parsed Date"])

    if trend_df.empty:
        return pd.DataFrame()

    trend_df["Month"] = (
        trend_df["Parsed Date"].dt.to_period("M").astype(str)
    )

    monthly = trend_df.groupby("Month").agg(
        Feedback_Count=("Feedback", "count"),
        Average_Quality=("Quality Score", "mean")
    ).reset_index()

    return monthly


# ==================================================
# CHART STYLE HELPERS
# ==================================================

BG_COLOR = CARD_BG
CHART_TEXT = TEXT_COLOR
CHART_MUTED = MUTED_COLOR


def style_axis(ax):

    ax.set_facecolor(BG_COLOR)

    ax.tick_params(
        colors=CHART_MUTED,
        labelsize=8
    )

    ax.xaxis.label.set_color(CHART_TEXT)
    ax.yaxis.label.set_color(CHART_TEXT)
    ax.title.set_color(CHART_TEXT)

    for spine in ax.spines.values():
        spine.set_color(BORDER_COLOR)

    ax.grid(
        axis="y",
        color=THEME["GRID"],
        alpha=0.45,
        linestyle="--"
    )


def make_bar_chart(series, title, horizontal=False):

    fig, ax = plt.subplots(figsize=(5, 2.65))

    fig.patch.set_facecolor(BG_COLOR)

    values = series.values
    labels = series.index.astype(str)

    if horizontal:

        bars = ax.barh(
            labels,
            values,
            color=PURPLE,
            height=0.55
        )

        ax.invert_yaxis()

        ax.tick_params(axis="y", labelsize=8)

    else:

        bars = ax.bar(
            labels,
            values,
            color=PURPLE,
            width=0.55
        )

        ax.tick_params(
            axis="x",
            rotation=20,
            labelsize=8
        )

    ax.set_title(
        title,
        fontsize=10,
        fontweight="bold",
        pad=12
    )

    style_axis(ax)

    ax.bar_label(
        bars,
        padding=3,
        color=CHART_TEXT,
        fontsize=8
    )

    fig.tight_layout()

    return fig


def make_line_chart(x, y, title, ylabel):

    fig, ax = plt.subplots(figsize=(5, 2.65))

    fig.patch.set_facecolor(BG_COLOR)

    ax.plot(
        x,
        y,
        marker="o",
        linewidth=2.2,
        markersize=5,
        color=PURPLE
    )

    ax.set_title(
        title,
        fontsize=10,
        fontweight="bold",
        pad=12
    )

    ax.set_ylabel(ylabel, fontsize=8)

    ax.tick_params(
        axis="x",
        rotation=25,
        colors=CHART_MUTED
    )

    style_axis(ax)

    fig.tight_layout()

    return fig


def make_donut_chart(series):

    fig, ax = plt.subplots(figsize=(4.5, 2.8))

    fig.patch.set_facecolor(BG_COLOR)

    chart_colors = [
        PURPLE,
        BLUE,
        PINK,
        CYAN,
        "#FBBF24"
    ]

    wedges, texts, autotexts = ax.pie(
        series.values,
        labels=series.index,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.78,
        colors=chart_colors,
        wedgeprops={
            "width": 0.42,
            "edgecolor": BG_COLOR,
            "linewidth": 2
        },
        textprops={
            "color": CHART_TEXT,
            "fontsize": 8
        }
    )

    for item in autotexts:
        item.set_color("white")
        item.set_fontsize(8)
        item.set_fontweight("bold")

    ax.set_facecolor(BG_COLOR)

    fig.tight_layout()

    return fig


# ==================================================
# PDF REPORT
# ==================================================

def generate_pdf_report(df):

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Feedback Quality Evaluator",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Feedback Analysis Summary Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Generated on: " + datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            ),
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 18))

    total = len(df)

    average_rating = pd.to_numeric(
        df["Rating"], errors="coerce"
    ).mean()

    average_quality = pd.to_numeric(
        df["Quality Score"], errors="coerce"
    ).mean()

    positive_count = (df["Sentiment"] == "Positive").sum()

    summary_data = [
        ["Metric", "Value"],
        ["Total Feedback", str(total)],
        [
            "Average Rating",
            f"{average_rating:.2f}/5"
            if pd.notna(average_rating) else "N/A"
        ],
        [
            "Average Quality Score",
            f"{average_quality:.2f}/100"
            if pd.notna(average_quality) else "N/A"
        ],
        ["Positive Feedback", str(positive_count)]
    ]

    story.append(
        Paragraph("Overall Summary", styles["Heading2"])
    )

    summary_table = Table(
        summary_data,
        colWidths=[250, 200]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(summary_table)
    story.append(Spacer(1, 18))

    for column, heading in [
        ("Sentiment", "Sentiment Distribution"),
        ("Quality Label", "Quality Level Distribution"),
        ("Category", "Feedback Category Distribution")
    ]:

        story.append(
            Paragraph(heading, styles["Heading2"])
        )

        counts = df[column].fillna("Unknown").value_counts()

        table_data = [[heading, "Number of Records"]]

        for label, count in counts.items():
            table_data.append([str(label), str(count)])

        table = Table(
            table_data,
            colWidths=[250, 200]
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 7)
            ])
        )

        story.append(table)
        story.append(Spacer(1, 16))

    monthly = prepare_monthly_trends(df)

    if not monthly.empty:

        story.append(
            Paragraph("Monthly Feedback Trend", styles["Heading2"])
        )

        chart_buffer = BytesIO()

        fig, ax = plt.subplots(figsize=(7, 3))

        ax.plot(
            monthly["Month"],
            monthly["Feedback_Count"],
            marker="o",
            color=PURPLE
        )

        ax.set_title("Feedback Records per Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Feedback Count")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

        fig.tight_layout()

        fig.savefig(
            chart_buffer,
            format="png",
            dpi=150
        )

        plt.close(fig)

        chart_buffer.seek(0)

        story.append(
            PDFImage(
                chart_buffer,
                width=6.5 * inch,
                height=2.8 * inch
            )
        )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Note: Sentiment analysis uses VADER. Feedback quality "
            "evaluation and category assignment use rule-based methods.",
            styles["Italic"]
        )
    )

    document.build(story)

    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0 10px;">
            <div style="font-size:42px;">📊</div>
            <h2 style="color:#C4B5FD !important; margin-bottom:3px;">
                Feedback AI
            </h2>
            <p style="color:#94A3B8 !important; font-size:12px;">
                Quality & Sentiment Analytics
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("🛠️ Technologies")

    st.markdown(
        """
        - Python
        - Streamlit
        - Pandas
        - NLTK VADER
        - Matplotlib
        - WordCloud
        - ReportLab
        """
    )

    st.divider()

    st.subheader("✨ Features")

    st.markdown(
        """
        - Sentiment Analysis
        - Quality Evaluation
        - Improvement Suggestions
        - Category Classification
        - Feedback Dashboard
        - Trend Analysis
        - Report Generation
        """
    )

    st.divider()

    st.caption("AI Feedback Quality Evaluator")
    st.caption("Light & Dark Theme Edition 💜")


# ==================================================
# APPEARANCE SELECTOR - TOP RIGHT
# ==================================================

header_col, appearance_col = st.columns([5, 1])

with appearance_col:

    selected_theme = st.selectbox(
        "🎨 Appearance",
        ["Dark", "Light"],
        index=["Dark", "Light"].index(
            st.session_state.app_theme
        ),
        key="appearance_selector"
    )

    if selected_theme != st.session_state.app_theme:

        st.session_state.app_theme = selected_theme
        st.rerun()


# ==================================================
# MAIN HEADER
# ==================================================

st.markdown(
    """
    <div class="dashboard-header">
        <h2>📊 AI Feedback Quality Evaluator</h2>
        <p>
            Understand feedback sentiment, evaluate quality,
            and discover meaningful insights from user responses.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# MAIN TABS
# ==================================================

overview_tab, analysis_tab, dashboard_tab = st.tabs(
    [
        "🏠 Project Overview",
        "📝 Feedback Analysis",
        "📈 Dashboard"
    ]
)


# ==================================================
# PROJECT OVERVIEW
# ==================================================

with overview_tab:

    st.header("About the Project")

    st.write(
        "The AI Feedback Quality Evaluator is a Python-based "
        "application designed to analyze written feedback. "
        "It uses sentiment analysis to identify whether feedback "
        "is positive, negative, or neutral. It also applies a "
        "rule-based scoring method to estimate feedback quality "
        "and provides suggestions to make feedback more useful."
    )

    st.subheader("🎯 Objectives")

    st.markdown(
        """
        - Analyze the sentiment expressed in written feedback.
        - Evaluate feedback using length, specificity, clarity,
          and actionable suggestions.
        - Provide suggestions to improve feedback quality.
        - Group feedback into meaningful categories using keywords.
        - Analyze feedback patterns over time.
        - Generate downloadable PDF reports.
        - Present results through an interactive dashboard.
        """
    )

    st.subheader("⚙️ Methodology")

    st.write(
        "The application accepts feedback text from the user. "
        "The text is processed using VADER for sentiment analysis. "
        "A rule-based scoring system evaluates feedback quality. "
        "Keyword matching assigns a feedback category. Saved "
        "feedback records are used to calculate monthly trends "
        "and generate downloadable reports."
    )

    st.info(
        "Sentiment analysis uses VADER. Feedback quality scoring "
        "and category identification use rule-based methods. "
        "The project does not claim to use a separately trained "
        "machine learning model."
    )


# ==================================================
# FEEDBACK ANALYSIS
# ==================================================

with analysis_tab:

    st.header("📝 Analyze Your Feedback")

    st.write(
        "Enter feedback below to understand its sentiment "
        "and evaluate its quality."
    )

    feedback_text = st.text_area(
        "Your Feedback",
        height=150,
        placeholder="Write your feedback here..."
    )

    rating = st.slider(
        "Overall Rating",
        min_value=1,
        max_value=5,
        value=3
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "✨ Analyze Feedback",
            use_container_width=True
        ):

            if not feedback_text.strip():

                st.warning("Please enter feedback first.")

            else:

                sentiment, compound = analyze_sentiment(
                    feedback_text
                )

                quality_score, quality_label, breakdown = (
                    evaluate_quality(feedback_text)
                )

                category = classify_feedback_category(
                    feedback_text
                )

                suggestions = generate_suggestions(
                    feedback_text,
                    quality_score,
                    breakdown
                )

                st.session_state.latest_result = {
                    "Date & Time": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Feedback": feedback_text.strip(),
                    "Rating": rating,
                    "Sentiment": sentiment,
                    "Compound Score": compound,
                    "Quality Score": quality_score,
                    "Quality Label": quality_label,
                    "Category": category,
                    "Breakdown": breakdown,
                    "Suggestions": suggestions
                }

    with col2:

        if st.button(
            "🧹 Clear Current Analysis",
            use_container_width=True
        ):

            st.session_state.latest_result = None
            st.rerun()

    result = st.session_state.latest_result

    if result:

        st.divider()

        st.subheader("📋 Analysis Results")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Sentiment",
            result["Sentiment"]
        )

        col2.metric(
            "Quality Score",
            f'{result["Quality Score"]}/100'
        )

        col3.metric(
            "Quality Level",
            result["Quality Label"]
        )

        st.write("**Feedback Category:**", result["Category"])

        st.write(
            "**Compound Score:**",
            f'{result["Compound Score"]:.3f}'
        )

        st.subheader("📊 Quality Breakdown")

        breakdown_df = pd.DataFrame({
            "Component": list(result["Breakdown"].keys()),
            "Score": list(result["Breakdown"].values())
        })

        fig = make_bar_chart(
            breakdown_df.set_index("Component")["Score"],
            "Quality Breakdown",
            horizontal=True
        )

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.subheader("💡 Improvement Suggestions")

        for suggestion in result["Suggestions"]:
            st.write(f"• {suggestion}")

        if st.button(
            "💾 Save Feedback to History",
            use_container_width=True
        ):

            new_record = {
                column: result[column]
                for column in COLUMNS
            }

            history = load_history()

            history = pd.concat(
                [
                    history,
                    pd.DataFrame([new_record])
                ],
                ignore_index=True
            )

            save_history(history)

            st.session_state.feedback_history = history

            st.success("Feedback saved successfully!")


# ==================================================
# DASHBOARD
# ==================================================

with dashboard_tab:

    st.markdown(
        """
        <div class="dashboard-header">
            <h2>✨ Analytics Overview</h2>
            <p>
                Monitor feedback performance and explore
                important insights in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_history()

    st.session_state.feedback_history = df.copy()

    if df.empty:

        st.info(
            "No saved feedback available. Analyze and save "
            "some feedback to populate your dashboard."
        )

    else:

        df["Rating"] = pd.to_numeric(
            df["Rating"], errors="coerce"
        )

        df["Quality Score"] = pd.to_numeric(
            df["Quality Score"], errors="coerce"
        )

        df["Compound Score"] = pd.to_numeric(
            df["Compound Score"], errors="coerce"
        )

        df["Category"] = df["Category"].fillna(
            "General / Other"
        )

        total_feedback = len(df)

        average_rating = df["Rating"].mean()

        average_quality = df["Quality Score"].mean()

        positive_count = (
            df["Sentiment"] == "Positive"
        ).sum()

        negative_count = (
            df["Sentiment"] == "Negative"
        ).sum()

        neutral_count = (
            df["Sentiment"] == "Neutral"
        ).sum()

        # ------------------------------------------
        # KPI CARDS
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">KEY PERFORMANCE INDICATORS</div>',
            unsafe_allow_html=True
        )

        k1, k2, k3, k4 = st.columns(4)

        with k1:

            st.metric(
                "📩 Total Feedback",
                total_feedback
            )

        with k2:

            st.metric(
                "⭐ Average Rating",
                f"{average_rating:.2f}/5"
                if pd.notna(average_rating) else "N/A"
            )

        with k3:

            st.metric(
                "🎯 Average Quality",
                f"{average_quality:.1f}/100"
                if pd.notna(average_quality) else "N/A"
            )

        with k4:

            st.metric(
                "😊 Positive Feedback",
                int(positive_count)
            )

        st.caption(
            f"Sentiment overview: {positive_count} positive · "
            f"{negative_count} negative · {neutral_count} neutral"
        )

        st.divider()

        # ------------------------------------------
        # SEARCH AND FILTER
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">FEEDBACK EXPLORER</div>',
            unsafe_allow_html=True
        )

        search_col, sentiment_col, quality_col = st.columns(
            [2, 1, 1]
        )

        with search_col:

            search_text = st.text_input(
                "🔎 Search feedback",
                placeholder="Search using a keyword..."
            )

        with sentiment_col:

            sentiment_options = ["All"] + sorted(
                df["Sentiment"].dropna().astype(str).unique().tolist()
            )

            selected_sentiment = st.selectbox(
                "Sentiment",
                sentiment_options
            )

        with quality_col:

            quality_options = ["All"] + sorted(
                df["Quality Label"].dropna().astype(str).unique().tolist()
            )

            selected_quality = st.selectbox(
                "Quality",
                quality_options
            )

        filtered_df = df.copy()

        if search_text.strip():

            filtered_df = filtered_df[
                filtered_df["Feedback"].astype(str).str.contains(
                    search_text,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        if selected_sentiment != "All":

            filtered_df = filtered_df[
                filtered_df["Sentiment"] == selected_sentiment
            ]

        if selected_quality != "All":

            filtered_df = filtered_df[
                filtered_df["Quality Label"] == selected_quality
            ]

        st.caption(
            f"Displaying {len(filtered_df)} of {total_feedback} records"
        )

        st.dataframe(
            filtered_df[COLUMNS],
            use_container_width=True,
            hide_index=True,
            height=260
        )

        st.divider()

        # ------------------------------------------
        # SENTIMENT ANALYSIS
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">SENTIMENT INSIGHTS</div>',
            unsafe_allow_html=True
        )

        sentiment_counts = df["Sentiment"].value_counts()

        sentiment_col1, sentiment_col2 = st.columns(2)

        with sentiment_col1:

            fig = make_bar_chart(
                sentiment_counts,
                "Sentiment Distribution"
            )

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with sentiment_col2:

            fig = make_donut_chart(sentiment_counts)

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.divider()

        # ------------------------------------------
        # QUALITY AND RATING
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">QUALITY & RATING ANALYSIS</div>',
            unsafe_allow_html=True
        )

        quality_col, rating_col = st.columns(2)

        with quality_col:

            quality_counts = df["Quality Label"].value_counts()

            fig = make_bar_chart(
                quality_counts,
                "Feedback Quality Levels"
            )

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with rating_col:

            rating_counts = (
                df["Rating"]
                .dropna()
                .astype(int)
                .value_counts()
                .sort_index()
            )

            fig = make_bar_chart(
                rating_counts,
                "Customer Rating Distribution"
            )

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        st.divider()

        # ------------------------------------------
        # CATEGORY ANALYSIS
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">CATEGORY INSIGHTS</div>',
            unsafe_allow_html=True
        )

        category_counts = df["Category"].value_counts()

        category_col1, category_col2 = st.columns([1.7, 1])

        with category_col1:

            fig = make_bar_chart(
                category_counts,
                "Feedback by Category",
                horizontal=True
            )

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with category_col2:

            st.subheader("Category Summary")

            for category, count in category_counts.items():

                percentage = count / total_feedback * 100

                st.markdown(
                    f"""
                    <div class="custom-card">
                        <div class="custom-card-title">{category}</div>
                        <div class="custom-card-value">{count}</div>
                        <div class="custom-card-note">
                            {percentage:.1f}% of total feedback
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.caption(
            "Category identification uses predefined keyword matching."
        )

        st.divider()

        # ------------------------------------------
        # WORD CLOUD
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">COMMON FEEDBACK WORDS</div>',
            unsafe_allow_html=True
        )

        all_feedback = " ".join(
            df["Feedback"].dropna().astype(str)
        )

        if all_feedback.strip():

            try:

                wordcloud = generate_wordcloud(all_feedback)

                fig, ax = plt.subplots(figsize=(8, 3))

                fig.patch.set_facecolor(BG_COLOR)

                ax.set_facecolor(BG_COLOR)

                ax.imshow(
                    wordcloud,
                    interpolation="bilinear"
                )

                ax.axis("off")

                fig.tight_layout()

                st.pyplot(
                    fig,
                    use_container_width=True
                )

                plt.close(fig)

            except Exception as error:

                st.info(
                    f"Word Cloud could not be generated: {error}"
                )

        st.divider()

        # ------------------------------------------
        # MONTHLY TREND ANALYSIS
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">MONTHLY PERFORMANCE</div>',
            unsafe_allow_html=True
        )

        monthly_trends = prepare_monthly_trends(df)

        if not monthly_trends.empty:

            trend_col1, trend_col2 = st.columns(2)

            with trend_col1:

                fig = make_line_chart(
                    monthly_trends["Month"],
                    monthly_trends["Feedback_Count"],
                    "Monthly Feedback Volume",
                    "Feedback Count"
                )

                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            with trend_col2:

                fig = make_line_chart(
                    monthly_trends["Month"],
                    monthly_trends["Average_Quality"],
                    "Monthly Average Quality",
                    "Quality Score"
                )

                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            st.subheader("Monthly Trend Details")

            display_monthly = monthly_trends.rename(
                columns={
                    "Month": "Month",
                    "Feedback_Count": "Feedback Count",
                    "Average_Quality": "Average Quality Score"
                }
            )

            st.dataframe(
                display_monthly,
                use_container_width=True,
                hide_index=True,
                height=180
            )

        else:

            st.info(
                "Valid feedback dates are needed for monthly trends."
            )

        st.divider()

        # ------------------------------------------
        # DOWNLOAD REPORTS
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">EXPORT & DOWNLOAD</div>',
            unsafe_allow_html=True
        )

        download_col1, download_col2 = st.columns(2)

        with download_col1:

            csv_data = (
                filtered_df[COLUMNS]
                .to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name="feedback_analysis.csv",
                mime="text/csv",
                use_container_width=True
            )

        with download_col2:

            excel_buffer = BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                filtered_df[COLUMNS].to_excel(
                    writer,
                    index=False,
                    sheet_name="Feedback Analysis"
                )

            st.download_button(
                "📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name="feedback_analysis.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True
            )

        try:

            pdf_data = generate_pdf_report(df)

            st.download_button(
                "📄 Download Complete PDF Report",
                data=pdf_data,
                file_name="AI_Feedback_Analysis_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as error:

            st.error(f"PDF generation error: {error}")

        summary_report = f"""
AI FEEDBACK QUALITY EVALUATOR - SUMMARY REPORT

Total Feedback Records: {total_feedback}

Average Rating: {average_rating:.2f}/5

Average Quality Score: {average_quality:.2f}/100

Positive Feedback: {positive_count}
Negative Feedback: {negative_count}
Neutral Feedback: {neutral_count}

SENTIMENT DISTRIBUTION

{sentiment_counts.to_string()}

QUALITY LEVEL DISTRIBUTION

{quality_counts.to_string()}

CATEGORY DISTRIBUTION

{category_counts.to_string()}

Note:
Sentiment analysis uses VADER.
Feedback quality scoring and category assignment
use rule-based methods.
"""

        st.download_button(
            "📝 Download Text Summary",
            data=summary_report,
            file_name="feedback_summary_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.divider()

        # ------------------------------------------
        # CLEAR HISTORY
        # ------------------------------------------

        st.markdown(
            '<div class="section-label">HISTORY MANAGEMENT</div>',
            unsafe_allow_html=True
        )

        with st.expander("🗑️ Manage Feedback History"):

            st.warning(
                "Clearing history permanently deletes all saved "
                "feedback records from the CSV file."
            )

            confirm_clear = st.checkbox(
                "I understand and want to clear all saved feedback."
            )

            if st.button(
                "Clear All Feedback History",
                disabled=not confirm_clear
            ):

                if os.path.exists(HISTORY_FILE):
                    os.remove(HISTORY_FILE)

                st.session_state.feedback_history = pd.DataFrame(
                    columns=COLUMNS
                )

                st.session_state.latest_result = None

                st.success("Feedback history cleared successfully.")

                st.rerun()


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div class="app-footer">
        AI Feedback Quality Evaluator
        <br>
        Built with Python, Streamlit and Data Analytics 
    </div>
    """,
    unsafe_allow_html=True
)

# python -m streamlit run 📊_Feedback_Analysis.py