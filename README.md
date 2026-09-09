A Python application that automates repetitive SEO tasks:

Extracts content from a URL, raw article text, or a simple topic prompt.
Analyses readability, heading hierarchy, image alt tags, link structure, and thin‑content issues.
Generates primary/secondary keywords with TF‑IDF scoring and classifies search intent.
Calculates a 0‑100 SEO score using configurable weighted criteria.
Uses Google Gemini (or OpenAI/Groq) to create SEO‑optimized meta titles, meta descriptions, heading outlines, and AI‑rewritten content while preserving the original intent.
Shows before‑and‑after metrics, issue breakdowns, and actionable recommendations.
Persists every audit in a local SQLite database (seo_history.db).
Exports a professional PDF, Markdown, or JSON report with a single click.
The UI is built with Streamlit, offering an intuitive dashboard with theme support (light/dark).

Quick Start
powershell

# 1️⃣ Clone / open the project folder
cd "C:\Users\Dhruvika Jandhyala\OneDrive\Desktop\SEO Automation"
# 2️⃣ (Optional) create a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell
# .\venv\Scripts\activate.bat  # CMD
# 3️⃣ Install dependencies
pip install --upgrade pip
pip install \
    streamlit \
    google-generativeai \
    scikit-learn \
    pandas \
    plotly \
    requests \
    tqdm
# 4️⃣ (Optional) set a Gemini API key for the LLM features
$Env:GEMINI_API_KEY = "<YOUR_GEMINI_API_KEY>"
# 5️⃣ Launch the dashboard
streamlit run app.py
Open the URL shown in the console (usually http://localhost:8501).

Usage Walk‑through
Sidebar – Choose Input Source (URL / Raw Text / Topic), paste / type your content, set a Primary Target Keyword, and optionally paste a Gemini API key.
Scoring Weights – Use the ⚖️ Customize Scoring Weights expander to give more importance to the pillars you care about.
Run Audit – Click 🚀 Run Comprehensive SEO Audit.
Dashboard Tabs –
📊 Overview & Score – overall score gauge, pillar breakdown, SERP preview.
🔑 Keywords & Intent – top TF‑IDF terms, intent distribution, LSI gaps.
⚠️ SEO Audit Issues – critical/warning/info issues with fix checklist.
🏷️ SERP Meta Generator – AI‑generated title & description options.
🌳 Content Structure – current vs recommended heading hierarchy.
✨ AI Content Optimizer – before/after content comparison and metric deltas.
📜 Project History – view, load, or delete past audits (stored in SQLite).
📥 Export Reports – one‑click download of PDF, Markdown, or JSON.
Architecture Snapshot

Input (URL / Text / Topic)
    │
    ▼
┌─────────────────────┐
│  ContentExtractor   │   # requests + BeautifulSoup
└───────┬─────────────┘
        │
        ▼
┌─────────────────────┐
│  Analyzer Suite     │   # keyword, readability, headings
│  • KeywordAnalyzer  │   # TF‑IDF (scikit‑learn)
│  • ContentAnalyzer  │   # textstat readability
│  • SEOScorer        │   # weighted 0‑100 score
└───────┬─────────────┘
        │
        ▼
┌─────────────────────┐
│   LLM Service       │   # Google Gemini (fallback heuristics)
│   • Meta titles
│   • Descriptions
│   • Outline
│   • Content rewrite
└───────┬─────────────┘
        │
        ▼
┌─────────────────────┐
│  RecommendationEngine│   # issue detection & action items
└───────┬─────────────┘
        │
        ▼
┌─────────────────────┐
│   Streamlit UI      │   # interactive dashboard, theme toggle
│   • History DB      │   # SQLite storage
│   • Exporter        │   # PDF (ReportLab), MD, JSON
└─────────────────────┘
Testing
A minimal unit‑test suite lives in tests/test_seo_pipeline.py. Run it with:

powershell

python -m unittest discover -s tests
All core components (extractor, analyzers, scorer, generators, optimizer, recommendation engine) are covered.

Extending the Platform
Add new LLM providers – extend llm/llm_service.py with the appropriate client and update the prompt templates.
Custom scoring – modify config.py or expose additional sliders in the sidebar.
More export formats – plug‑in additional exporters in utils/exporter.py (e.g., CSV, Word).
Deploy – the Streamlit app can be deployed to Streamlit Community Cloud, Azure App Service, or any Docker container.
License & Credits
© 2026 Dhruvika Jandhyala. MIT License.

Built with:

Streamlit – interactive Python web apps.
Google Gemini – generative LLM for SEO copy.
scikit‑learn – TF‑IDF keyword extraction.
textstat – readability metrics.
ReportLab – PDF generation.
plotly – interactive charts.
