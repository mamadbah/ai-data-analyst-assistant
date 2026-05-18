# AI Data Analyst Assistant

Smart AI-powered dataset analysis and visualization platform built with Streamlit and OpenAI.

---

# Project Overview

The AI Data Analyst Assistant is an intelligent web-based application designed to help users analyze datasets using artificial intelligence. The system combines data processing, statistical visualization, chatbot interaction, voice assistance, and AI reasoning to provide automated insights from uploaded datasets.

Users can upload CSV or Excel datasets, ask analytical questions using text or voice input, generate visualizations, and download PDF reports containing analysis results.

---

# Features

- Upload CSV and Excel datasets
- AI-powered chatbot for dataset analysis
- Voice assistant support
- Automatic dataset preview
- Statistical analysis and visualizations
- AI-generated insights and recommendations
- Downloadable PDF reports
- Chat history and analysis tracking
- Interactive Streamlit dashboard

---

# System Architecture

The AI Data Analyst Assistant follows an agentic AI workflow architecture composed of multiple layers:

## 1. User Layer
The user interacts with the system through:
- Dataset upload
- Text input
- Voice input
- Report download

## 2. Data Processing Layer
The system processes uploaded datasets using:
- Pandas
- NumPy

This layer handles:
- Dataset validation
- Data loading
- Missing value detection
- Statistical preprocessing

## 3. AI Reasoning Layer
The OpenAI API performs:
- Dataset understanding
- Natural language processing
- AI reasoning
- Insight generation
- Question answering

## 4. Visualization Layer
Charts and visualizations are generated using:
- Matplotlib
- Seaborn

Examples:
- Histograms
- Correlation charts
- Bar charts
- Distribution plots

## 5. Output Layer
The system provides:
- AI-generated responses
- Visualizations
- PDF reports
- Chat history

---

# Technologies and Libraries Used

| Technology / Library | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application framework |
| Pandas | Dataset processing and analysis |
| NumPy | Numerical computations |
| Matplotlib | Data visualization |
| Seaborn | Statistical charts |
| OpenAI API | AI reasoning and chatbot |
| ReportLab | PDF report generation |
| SpeechRecognition | Voice assistant support |
| PyArrow | Data handling optimization |

---

# Project Structure

```bash
AI-DATA-ANALYST-AGENT/
│
├── .streamlit/
│   └── secrets.toml
│
├── data/
│
├── reports/
│
├── utils/
│   ├── analyzer.py
│   └── insights.py
│
├── app.py
├── requirements.txt
├── README.md
├── analysis_history.json
├── chat_history.json
└── LICENSE


Installation Guide
Step 1 — Clone Repository
git clone <your_repository_link>
cd AI-DATA-ANALYST-AGENT

Step 2 — Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Mac/Linux
python3 -m venv venv
source venv/bin/activate

Step 3 — Install Dependencies
pip install -r requirements.txt
OpenAI API Setup

Create the following file:

.streamlit/secrets.toml

Add your OpenAI API key:

OPENAI_API_KEY="your_openai_api_key"
Running the Application

Start the Streamlit application:

streamlit run app.py

The application will open in your browser at:

http://localhost:8501
How the System Works
User uploads a dataset (CSV or Excel)
System validates the dataset
Dataset is loaded using Pandas
Initial visualizations are generated
User asks analytical questions
OpenAI processes dataset context and questions
AI generates insights and recommendations
Results are displayed on the dashboard
User downloads PDF report
Chatbot Capabilities

The AI chatbot can:

Detect missing values
Identify duplicates
Generate dataset summaries
Recommend cleaning actions
Explain statistical trends
Generate AI insights
Answer user questions about datasets

Example questions:

"Is this dataset suitable for analysis?"
"Are there missing values?"
"Generate insights about customer behavior."
"What trends can you identify?"
PDF Report Generation

The system generates downloadable PDF reports containing:

Dataset summary
Statistical analysis
AI-generated insights
Visualizations
Recommendations

PDF reports are created using ReportLab.

Voice Assistant

The application supports voice-based interaction using SpeechRecognition.

Users can:

Speak analytical questions
Receive AI-generated answers
Improve accessibility and user interaction
Responsible AI Considerations

The AI Data Analyst Assistant is designed as a support tool and should not replace professional judgment.

Important considerations:

AI-generated insights may occasionally contain inaccuracies
Users should verify analytical conclusions
Sensitive datasets should not be uploaded
Dataset bias may affect generated insights
Future Improvements

Planned future enhancements include:

Real-time dashboard analytics
Multi-agent AI workflow
Database integration
Advanced predictive analytics
User authentication system
Cloud deployment support
Author

Developed by Mamadou Djouhe Bah

License


This project is for educational and academic purposes.
