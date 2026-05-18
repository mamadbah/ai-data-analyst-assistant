import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import base64
import tempfile
import json
import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from openai import OpenAI
from utils.analyzer import analyze_data
from utils.insights import generate_insights
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Data Analyst",
    layout="wide"
)

st.markdown("""
<style>
.stDownloadButton {
    margin-bottom: 80px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Main page spacing */
.main .block-container {
    padding-bottom: 140px;
}

/* Keep chat input above footer */
.stChatInput {
    bottom: 90px !important;
}

/* Fixed Footer */
.footer {
    position: fixed;
    bottom: 0;
    left: 250px;
    width: calc(100% - 250px);
    background: #000814;
    color: white;
    text-align: center;
    padding: 10px;
    z-index: 999999;
    border-top: 1px solid #1d4ed8;
}

/* Prevent footer flicker */
[data-testid="stAppViewContainer"] {
    overflow-x: hidden;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* Add space at bottom of page */
.main .block-container {
    padding-bottom: 180px;
}

/* Move chat input above footer */
.stChatInput {
    bottom: 90px !important;
}

/* Footer */
.footer {
    position: fixed;
    bottom: 0;
    left: 250px;
    width: calc(100% - 250px);
    background-color: #000814;
    color: white;
    text-align: center;
    padding: 10px;
    z-index: 999;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* Fix chat input width and position */
.stChatInput {
    position: fixed !important;
    bottom: 85px !important;
    left: 290px !important;
    width: calc(100% - 340px) !important;
    z-index: 998;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* USER BUTTON */
div[data-testid="stPopover"] button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 6px 15px rgba(37,99,235,0.35) !important;
}

/* HOVER */
div[data-testid="stPopover"] button:hover {
    transform: translateY(-2px);
    transition: 0.2s ease;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* SIDEBAR BACKGROUND */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1e3a8a 0%,
        #2563eb 50%,
        #3b82f6 100%
    ) !important;
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* INFO BOX */
section[data-testid="stSidebar"] .stAlert {
    background-color: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
}

/* SIDEBAR BUTTONS */
section[data-testid="stSidebar"] button {
    border-radius: 10px !important;
}

/* CHAT HISTORY BOXES */
section[data-testid="stSidebar"] .stExpander {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FULL WIDTH CSS ----------------
st.markdown("""
<style>

/* Make page full width */
.block-container {
    max-width: 100% !important;
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

          

                      


/* Prevent centered layout */
.main .block-container {
    max-width: 100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ================= RESTORE DATASET =================
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# ================= RESTORE SESSION =================
if os.path.exists("user_session.json"):
    with open("user_session.json", "r") as f:
        session_data = json.load(f)
        st.session_state.logged_in = session_data.get("logged_in", False)
        st.session_state.user_email = session_data.get("user_email", "")

# ---------------- CHAT HISTORY ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


# ================= CONTINUOUS CONVERSATION =================
if "listening" not in st.session_state:
    st.session_state.listening = False

# ---------------- HISTORY STORAGE ----------------

HISTORY_FILE = "analysis_history.json"

# Create file if it does not exist
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# Load history
with open(HISTORY_FILE, "r") as f:
    saved_history = json.load(f)

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = saved_history

# ================= CHAT HISTORY STORAGE =================
CHAT_HISTORY_FILE = "chat_history.json"
if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump([], f)

with open(CHAT_HISTORY_FILE, "r") as f:
    saved_chat_history = json.load(f)

if "saved_chat_history" not in st.session_state:
    st.session_state.saved_chat_history = saved_chat_history

    
# ---------------- ANALYSIS HISTORY ----------------

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    # ---------------- CUSTOM CSS ----------------
    st.markdown("""
    <style>

    .stApp {
        background-color: white;
    }

    .login-title {
        font-size: 60px;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: center;
        line-height: 1.1;
        color: #2E2E3A;
    }

    .subtitle {
        color: gray;
        font-size: 22px;
        text-align: center;
        margin-top: 0;
        margin-bottom: 10px;
    }

    .subtext {
        color: gray;
        font-size: 17px;
        text-align: center;
        margin-top: 0;
        margin-bottom: 50px;
    }

    .footer-text {
        color: gray;
        margin-top: 20px;
        font-size: 14px;
        text-align: center;
    }

    .stButton button {
    background-color: #5B2C83;
    color: white;
    width: 100%;
    border-radius: 8px;
    height: 45px;
    border: none;
    font-size: 16px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton button:hover {
    background-color: #6D36A0;
    color: white;
    border: none;
}

.stButton button:focus {
    outline: none;
    box-shadow: none;
}

    .stTextInput input {
        height: 45px;
        border-radius: 8px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- LAYOUT ----------------
    col1, col2 = st.columns([1.3, 1])

    # ---------------- LEFT SIDE ----------------
    with col1:

        st.markdown("<br><br>", unsafe_allow_html=True)

        image = PILImage.open("login_image.webp")
        st.image(image, width=950)

    # ---------------- RIGHT SIDE ----------------
    with col2:

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

        # TITLE
        st.markdown(
            """
            <h1 class="login-title">
                Data Analytic Assistant
                <span style='color:#78D64B;'>AI</span>
            </h1>
            """,
            unsafe_allow_html=True
        )

        # SUBTITLE
        st.markdown(
            """
            <p class="subtitle">
                Smart AI-powered Data Analytics Platform
            </p>
            """,
            unsafe_allow_html=True
        )

        # SUBTEXT
        st.markdown(
            """
            <p class="subtext">
                Reliable, scalable, secure AI for dreamers
            </p>
            """,
            unsafe_allow_html=True
        )

        # EMAIL INPUT
        email = st.text_input(
            "Enter your email",
            placeholder="email@example.com"
        )

        # LOGIN BUTTON
        if st.button("Login with Email"):

            if email:

                st.session_state.logged_in = True
                st.session_state.user_email = email

                # SAVE LOGIN
                with open("user_session.json", "w") as f:
                    json.dump({
                        "logged_in": True,
                        "user_email": email
                    }, f)
                st.success("Login successful")
                

                st.rerun()
            else:
                st.error("Please enter your email")
                
                

        # FOOTER
        st.markdown(
            """
            <p class="footer-text">
                By signing up, you agree to our Terms of Service and Privacy Policy
            </p>
            """,
            unsafe_allow_html=True
        )

    # STOP LOGIN PAGE
    st.stop()

    # USER IS LOGGED IN


# ---------------- TOP RIGHT USER MENU ----------------

top1, top2 = st.columns([9, 1])

with top2:

    with st.popover("👤 User"):

        user_email = st.session_state.get(
            "user_email",
            "user@email.com"
        )

        st.markdown("### 👤 Profile")

        st.write(user_email)

        st.divider()

      

        # LOG OUT BUTTON

        if st.button(
            "🔓 Sign Out",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user_email = ""
            # REMOVE SAVED SESSION
            if os.path.exists("user_session.json"):
                os.remove("user_session.json")

            
            st.rerun()

def generate_pdf_report(
    df,
    analysis,
    insights,
    recommendations,
    health_score,
    chart_path=None
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    # TITLE
    title = Paragraph(
        "AI Data Analyst Full Report",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # HEALTH SCORE
    health_title = Paragraph(
        "Dataset Health Score",
        styles['Heading2']
    )
    elements.append(health_title)

    health_text = Paragraph(
        f"<b>Overall Quality Score:</b> {health_score:.1f}%",
        styles['BodyText']
    )

    elements.append(health_text)
    elements.append(Spacer(1, 20))

    # DATASET PREVIEW
    preview_title = Paragraph(
        "Dataset Preview",
        styles['Heading2']
    )

    elements.append(preview_title)
    
    preview_data = [df.head().columns.tolist()] + df.head().values.tolist()

    preview_table = Table(
        preview_data,
        repeatRows=1
    )


    preview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    elements.append(preview_table)
    elements.append(Spacer(1, 20))

    # DATASET ANALYSIS
    analysis_title = Paragraph(
        "Dataset Analysis",
        styles['Heading2']
    )

    elements.append(analysis_title)

    analysis_data = [analysis.columns.tolist()] + analysis.values.tolist()

    analysis_table = Table(
        analysis_data,
        repeatRows=1
    )

    analysis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    elements.append(analysis_table)
    elements.append(Spacer(1, 20))

    # AI INSIGHTS
    insights_title = Paragraph(
        "AI Insights",
        styles['Heading2']
    )

    elements.append(insights_title)

    for insight in insights:
        elements.append(
            Paragraph(
                f"• {insight}",
                styles['BodyText']
            )
        )

    elements.append(Spacer(1, 20))

    # RECOMMENDATIONS
    recommendations_title = Paragraph(
        "Smart Recommendations",
        styles['Heading2']
    )

    elements.append(recommendations_title)

    for recommendation in recommendations:
        elements.append(
            Paragraph(
                f"• {recommendation}",
                styles['BodyText']
            )
        )

    elements.append(Spacer(1, 20))

    # VISUALIZATION
    if chart_path:
        chart_title = Paragraph(
            "Data Visualization",
             styles['Heading2']
        )

        elements.append(chart_title)

        if os.path.exists(chart_path):
            img = Image(
                 chart_path,
                 width=450,
                 height=220
            )
            elements.append(img)

        else:
             elements.append(
                  Paragraph(
                      "Chart image not found.",
                      styles['BodyText']
                      
                  )
             )
        elements.append(Spacer(1, 20))
            

    

    # ================= CHAT HISTORY =================
    chat_title = Paragraph(
        "Chat Conversations",
        styles['Heading2']
    )

    elements.append(chat_title)
    elements.append(Spacer(1, 10))
    for msg in st.session_state.chat_history:
        role = msg["role"].capitalize()
        content = msg["content"]
        chat_text = Paragraph(
            f"<b>{role}:</b> {content}",
            styles['BodyText']
        )

        elements.append(chat_text)
        elements.append(Spacer(1, 8))

    # ================= CHATBOT HISTORY =================
    chatbot_title = Paragraph(
        "AI Chatbot Conversations",
        styles['Heading2']
    )
    elements.append(chatbot_title)
    elements.append(Spacer(1, 10))

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            role_name = "User"
        else:
            role_name = "AI Assistant"
        chatbot_text = Paragraph(
            f"<b>{role_name}:</b> {msg['content']}",
            styles['BodyText']
        )

        elements.append(chatbot_text)
        elements.append(Spacer(1, 8))

    # ================= VOICE HISTORY =================
    voice_title = Paragraph(
        "Voice Assistant History",
        styles['Heading2']
    )

    elements.append(voice_title)
    elements.append(Spacer(1, 10))
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            voice_text = Paragraph(
                f"🎤 User: {msg['content']}",
                styles['BodyText']
            )

        else:
            voice_text = Paragraph(
                f"🤖 AI: {msg['content']}",
                styles['BodyText']
            )

        elements.append(voice_text)
        elements.append(Spacer(1, 6))

    # FINALIZE PDF
    doc.build(elements)


    pdf = buffer.getvalue()

    buffer.close()

    return pdf
st.sidebar.markdown("""
<div style='text-align:center;'>
    <img src='data:image/png;base64,{}' width='140'>
</div>
""".format(get_base64_image("ai_logo.png")), unsafe_allow_html=True)
st.sidebar.title("AI Agent Dashboard")
st.sidebar.info(
    "This AI agent analyzes datasets and generates insights automatically."
)

# ================= CONTINUOUS CONVERSATION =================
continuous_mode = st.sidebar.toggle(
    "🎙 Continuous Conversation",
    value=False
)
# ---------------- HISTORY SECTION ----------------

st.sidebar.markdown("---")
st.sidebar.subheader("📁 Analysis History")

if len(st.session_state.analysis_history) == 0:

    st.sidebar.write("No analysis yet")

else:

    for i, record in enumerate(st.session_state.analysis_history):

        with st.sidebar.expander(
            f"📄 {record['file_name']}"):

            if st.button(
                f"🗑 Delete",
                key=f"delete_{i}"
            ):
                st.session_state.analysis_history.pop(i)
                # UPDATE JSON FILE
                with open(HISTORY_FILE, "w") as f:
                    json.dump(st.session_state.analysis_history, f)
                st.rerun()
        

            st.write(f"Rows: {record['rows']}")
            st.write(f"Columns: {record['columns']}")

            st.markdown("### Insights")

            for insight in record["insights"]:
                st.write("•", insight)

            st.markdown("### Recommendations")

            for rec in record["recommendations"]:
                st.success(rec)

# ================= CHAT HISTORY SIDEBAR =================
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Chat History")
# USER QUESTIONS
with st.sidebar.expander("👤 User Questions", expanded=False):
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write("• " + message["content"])

# AI ANSWERS
with st.sidebar.expander("🤖 AI Answers", expanded=False):
    for message in st.session_state.chat_history:
        if message["role"] != "user":
            st.write("• " + message["content"])

st.markdown("""
<div style='text-align:center; margin-top:0px; margin-bottom:0px;'>

<h1 style='
font-size:55px;
font-weight:800;
color:#2D2D3A;
margin-bottom:0px;
'>
🤖 AI Data Analyst Assistant
</h1>

<h3 style='
color:gray;
font-weight:normal;
margin-top:0px;
margin-bottom:-5px;
'>
Smart AI-powered dataset analysis and visualization platform
</h3>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
display:flex;
justify-content:center;
align-items:center;
gap:30px;
flex-wrap:wrap;
font-size:18px;
margin-top:10px;
margin-bottom:15px;
text-align:center;
">

<span>📊 Analyze statistics</span>
<span>🔍 Detect patterns</span>
<span>🤖 Generate AI insights</span>
<span>📈 Visualize trends</span>
<span>💡 Receive recommendations</span>

</div>
""", unsafe_allow_html=True)

st.write("Upload a dataset for analysis")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"]
)
chart_path = None

file_to_load = None

if uploaded_file:

    # SAVE FILE
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.current_file = uploaded_file.name
    file_to_load = uploaded_file.name

elif st.session_state.current_file:
    file_to_load = st.session_state.current_file

# LOAD DATASET
if file_to_load:
    if file_to_load.endswith(".csv"):
        df = pd.read_csv(file_to_load)
    else:
        df = pd.read_excel(file_to_load)

    st.subheader("Dataset Preview")

    st.write(df.head())
    st.subheader("Dataset Analysis")
    analysis = analyze_data(df)
    st.write(analysis)
    st.subheader("AI Insights")
    insights, recommendations = generate_insights(df)
    # ---------------- SAVE TO HISTORY ----------------

    analysis_record = {
        "file_name": file_to_load,
        "rows": df.shape[0],
        "columns": df.shape[1],
        "insights": insights,
        "recommendations": recommendations
    }

# Avoid duplicates
    if analysis_record not in st.session_state.analysis_history:

        st.session_state.analysis_history.insert(0, analysis_record)

        # SAVE TO JSON FILE
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.analysis_history, f)

    for insight in insights:
        st.write("-", insight)
    st.subheader("Smart Recommendations")
    for recommendation in recommendations:
        st.success(recommendation)

    st.subheader("Dataset Health Score")
    missing_percentage = (
        df.isnull().sum().sum() /
        (df.shape[0] * df.shape[1])
    ) * 100

    health_score = 100 - missing_percentage
    st.metric(
        label="Dataset Quality Score",
        value=f"{health_score:.1f}%"
    )
    if health_score > 90:
        st.success("Excellent dataset quality")
    elif health_score > 70:
        st.warning("Moderate dataset quality")
    else:
        st.error("Poor dataset quality")


  
    # ================= DATA VISUALIZATION =================
    st.subheader("📊 Data Visualization")
    numeric_cols = df.select_dtypes(include=["number"]).columns
    all_cols = df.columns

    if len(numeric_cols) > 0:
        chart_type = st.selectbox(
            "Select Chart Type",
            {
                "Histogram",
                "Line Chart",
                "Scatter Plot",
                "Pie Chart",
                "Bar Chart"


            }
        )

        # ================= HISTOGRAM =================
        if chart_type == "Histogram":
            selected_col = st.selectbox(
                "Select Numeric Column",
                numeric_cols

            )

            fig, ax = plt.subplots(figsize=(5,5))

            ax.hist(
                df[selected_col].dropna(),
                bins=20,
                label=selected_col


            )

            ax.set_title(f"Distribution of {selected_col}")
            ax.set_xlabel(selected_col)
            ax.set_ylabel("Frequency")
            ax.legend()

            chart_path = "chart.png"
            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(
                    fig,
                     use_container_width=False
                )
        
            plt.close(fig)

        # ================= LINE CHART =================
        elif chart_type == "Line Chart":

            x_col = st.selectbox("Select X-Axis", all_cols)
            y_col = st.selectbox("Select Y-Axis", numeric_cols)
            fig, ax = plt.subplots(figsize=(5,5))

            ax.plot(
                df[x_col],
                df[y_col],
                marker="o",
                label=y_col

            )

            ax.set_title(f"{y_col} Trend")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.legend()

            chart_path = "chart.png"
            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(
                     fig,
                     use_container_width=False
                )

            plt.close(fig)

        # ================= SCATTER PLOT =================
        elif chart_type == "Scatter Plot":
            x_col = st.selectbox("Select X-Axis", numeric_cols)
            y_col = st.selectbox("Select Y-Axis", numeric_cols)
            fig, ax = plt.subplots(figsize=(5,5))

            ax.scatter(
                df[x_col],
                df[y_col],
                label=f"{x_col} vs {y_col}"

            )

            ax.set_title(f"{x_col} vs {y_col}")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.legend()

            chart_path = "chart.png"
            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(
                    fig,
                    use_container_width=False
                )
            plt.close(fig)

        # ================= PIE CHART =================
        elif chart_type == "Pie Chart":
            pie_col = st.selectbox(
                "Select Category Column",
                all_cols

            )

            pie_data = df[pie_col].value_counts().head(5)
            fig, ax = plt.subplots(figsize=(5,5))

            ax.pie(
                pie_data,
                labels=pie_data.index,
                autopct='%1.1f%%'



            )

            ax.set_title(f"{pie_col} Distribution")
            chart_path = "chart.png"
            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                 st.pyplot(
                      fig,
                      use_container_width=False
                 )
            plt.close(fig)

        # ================= BAR CHART =================
        elif chart_type == "Bar Chart":
            bar_col = st.selectbox(
                "Select Category Column",
                all_cols

            )

            bar_data = df[bar_col].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(5,5))

            ax.bar(
                bar_data.index,
                bar_data.values,
                label=bar_col

            )

            ax.set_title(f"{bar_col} Frequency")
            ax.set_xlabel(bar_col)
            ax.set_ylabel("Count")
            ax.legend()
            plt.xticks(rotation=45)
            chart_path = "chart.png"
            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(
                    fig,
                    use_container_width=False
                )
            plt.close(fig)

    pdf_data = generate_pdf_report(
       df,
       analysis,
       insights,
       recommendations,
       health_score,
        chart_path=chart_path
    )

    

    
    # ================= AI CHATBOT =================
    st.markdown("---")
    st.subheader("🤖 AI Dataset Chatbot")
    # ================= VOICE ASSISTANT =================
    st.markdown("### 🎤 Voice Assistant")
    voice_data = mic_recorder(
        start_prompt="🎙 Speak",
        stop_prompt="⏹ Stop",
        just_once=not continuous_mode
        
    )

    # ================= VOICE TO TEXT =================
    voice_text = ""
    if voice_data:
        audio_bytes = voice_data["bytes"]
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)

            # OPENAI SPEECH TO TEXT
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"

                )
            voice_text = transcript.text
            st.success(f"🎤 You said: {voice_text}")
    
    st.markdown("<div style='margin-bottom:120px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:80px;'></div>", unsafe_allow_html=True)


    # ================= MERGED CHAT INPUT =================

    typed_question = st.chat_input(
        "Ask anything about your dataset..."
    )
    user_question = typed_question or voice_text
    
    if user_question:
        # SAVE USER MESSAGE
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        # DATASET CONTEXT
        dataset_context = df.head(50).to_string()
        # SEND TO OPENAI
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are a professional AI Data Analyst.

                    Answer questions ONLY based on this dataset:

                    {dataset_context}

                    You are a conversational AI Data Analyst.
                    Maintain natural conversation flow.
                    Remember previous questions and answers.
                    If the user asks follow-up questions,
                    answer based on previous context.
                    Provide concise, intelligent,
                    and human-like explanations.
                    """
                },

                *st.session_state.chat_history
            ]
        )

        # GET AI REPLY
        ai_reply = response.choices[0].message.content

        # ================= AI VOICE RESPONSE =================
        tts = gTTS(ai_reply)
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        ) as fp:
            tts.save(fp.name)
            audio_file = open(fp.name, "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
        # ================= AUTO CONTINUE =================
        if continuous_mode:
             st.rerun()

        # SAVE AI REPLY
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": ai_reply
            }
        )

        # SAVE FULL CHAT SESSION
        chat_record = {
            "dataset": uploaded_file.name,
            "question": user_question,
            "answer": ai_reply
        }

        st.session_state.saved_chat_history.insert(0, chat_record)
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(st.session_state.saved_chat_history, f)

   

    # DISPLAY CHAT
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])




# ================= PDF DOWNLOAD =================

    
    st.download_button(
    label="Download PDF Report",
    data=pdf_data,
    file_name="AI_Data_Analysis_Report.pdf",
    mime="application/pdf"
    )



st.markdown("""
<div class="footer">
🚀 AI Data Analyst Assistant<br>
Developed by Mamadou Djouhe Bah
</div>
""", unsafe_allow_html=True)



