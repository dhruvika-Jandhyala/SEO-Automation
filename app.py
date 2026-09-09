import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

from config import DEFAULT_SCORING_WEIGHTS
from extractor.content_extractor import ContentExtractor
from analyzer.keyword_analyzer import KeywordAnalyzer
from analyzer.content_analyzer import ContentAnalyzer
from analyzer.seo_scorer import SEOScorer
from llm.llm_service import LLMService
from generators.meta_generator import MetaGenerator
from generators.keyword_generator import KeywordGenerator
from generators.heading_generator import HeadingGenerator
from generators.content_optimizer import ContentOptimizer
from recommendations.recommendation_engine import RecommendationEngine
from database.history_db import HistoryDatabase
from utils.exporter import ReportExporter

# Page Configuration
st.set_page_config(
    page_title="AI-Powered SEO Automation Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for SERP preview & cards
st.markdown("""
<style>
/* Theme selector – default to light */
.light-mode {
  --bg-color: #f8f9fa;
  --card-bg: #ffffff;
  --text-color: #212529;
  --primary: #1a73e8;
  --badge-critical-bg: #fee2e2; --badge-critical-fg: #991b1b;
  --badge-warning-bg: #fef3c7; --badge-warning-fg: #92400e;
  --badge-info-bg: #e0f2fe; --badge-info-fg: #075985;
}
.dark-mode {
  --bg-color: #212529;
  --card-bg: #2c2f33;
  --text-color: #e9ecef;
  --primary: #8ab4f8;
  --badge-critical-bg: #7f1d1d; --badge-critical-fg: #ffdad6;
  --badge-warning-bg: #7c5e10; --badge-warning-fg: #ffecb5;
  --badge-info-bg: #083344; --badge-info-fg: #cfefff;
}
body {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}
.serp-card {
  background-color: var(--card-bg);
  border: 1px solid #dfe1e5;
  border-radius: 8px;
  padding: 16px;
  font-family: arial, sans-serif;
  box-shadow: 0 1px 6px rgba(32,33,36,0.1);
  margin-bottom: 15px;
}
.serp-url { font-size: 14px; color: var(--text-color); line-height: 1.3; }
.serp-title { font-size: 20px; color: var(--primary); text-decoration: none; cursor: pointer; line-height: 1.3; font-weight: 400; margin-top: 4px; margin-bottom: 4px; }
.serp-desc { font-size: 14px; color: var(--text-color); line-height: 1.58; }
.badge-critical { background-color: var(--badge-critical-bg); color: var(--badge-critical-fg); padding: 4px 8px; border-radius: 4px; font-weight: bold; }
.badge-warning { background-color: var(--badge-warning-bg); color: var(--badge-warning-fg); padding: 4px 8px; border-radius: 4px; font-weight: bold; }
.badge-info { background-color: var(--badge-info-bg); color: var(--badge-info-fg); padding: 4px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar Theme Toggle
theme_choice = st.sidebar.selectbox("Theme", ["Light", "Dark"], index=0)
if theme_choice == "Dark":
    st.markdown("<script>document.body.classList.add('dark-mode');</script>", unsafe_allow_html=True)
else:
    st.markdown("<script>document.body.classList.add('light-mode');</script>", unsafe_allow_html=True)

# Initialize DB & Exporter
db = HistoryDatabase()
exporter = ReportExporter()

# Sidebar Configuration
st.sidebar.title("⚙️ SEO Engine Config")
st.sidebar.markdown("---")

# LLM API Configuration
st.sidebar.subheader("🤖 LLM Provider")
api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="Enter Google Gemini API Key for deep AI recommendations & content rewriting. Leave blank for fallback NLP heuristics.")

# Scoring Weights Customizer
with st.sidebar.expander("⚖️ Customize Scoring Weights", expanded=False):
    w_meta = st.slider("Metadata Quality", 0.0, 0.5, DEFAULT_SCORING_WEIGHTS["metadata_quality"], 0.05)
    w_kw = st.slider("Keyword Optimization", 0.0, 0.5, DEFAULT_SCORING_WEIGHTS["keyword_optimization"], 0.05)
    w_len = st.slider("Content Length", 0.0, 0.5, DEFAULT_SCORING_WEIGHTS["content_length"], 0.05)
    w_head = st.slider("Heading Hierarchy", 0.0, 0.5, DEFAULT_SCORING_WEIGHTS["heading_structure"], 0.05)
    w_read = st.slider("Readability Index", 0.0, 0.5, DEFAULT_SCORING_WEIGHTS["readability"], 0.05)
    w_intent = st.slider("Intent Alignment", 0.0, 0.5, DEFAULT_SCORING_WEIGHTS["intent_alignment"], 0.05)

custom_weights = {
    "metadata_quality": w_meta,
    "keyword_optimization": w_kw,
    "content_length": w_len,
    "heading_structure": w_head,
    "readability": w_read,
    "intent_alignment": w_intent
}

# Header Banner
st.title("⚡ AI-Powered SEO Automation Platform")
st.caption("Automate repetitive SEO tasks: content extraction, TF-IDF keyword research, SERP meta generation, issue auditing, and AI content optimization.")

# Project Input Form
with st.form("seo_analysis_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        input_type = st.radio("Input Source Type", ["URL Scraper", "Raw Article / Text", "Topic Prompt"], horizontal=True)
        if input_type == "URL Scraper":
            user_input = st.text_input("Webpage URL", placeholder="https://example.com/blog/seo-guide")
        elif input_type == "Raw Article / Text":
            user_input = st.text_area("Article Content", height=150, placeholder="Paste your article or draft markdown text here...")
        else:
            user_input = st.text_input("Topic Keyword / Idea", placeholder="e.g. Electric Vehicle Maintenance Tips")

    with col2:
        project_name = st.text_input("Project / Campaign Name", value="My SEO Audit")
        target_keyword = st.text_input("Primary Target Keyword", placeholder="e.g. SEO automation")
        submit_btn = st.form_submit_button("🚀 Run Comprehensive SEO Audit", use_container_width=True)

# Main Processing Logic
if submit_btn and user_input:
    with st.spinner("Extracting content, calculating TF-IDF metrics, auditing structure, and running AI engine..."):
        # 1. Extractor
        extractor = ContentExtractor()
        if input_type == "URL Scraper":
            extracted = extractor.extract_from_url(user_input)
        elif input_type == "Raw Article / Text":
            extracted = extractor.extract_from_text(user_input)
        else:
            extracted = extractor.extract_from_topic(user_input)

        if not extracted.get("success"):
            st.error(extracted.get("error", "Failed to extract content."))
            st.stop()

        raw_text = extracted["raw_text"]
        meta_title = extracted["meta_title"]
        meta_desc = extracted["meta_description"]
        headings = extracted["headings"]
        images = extracted["images"]
        links = extracted["links"]
        word_count = extracted["word_count"]

        # 2. Analyzers
        kw_analyzer = KeywordAnalyzer()
        content_analyzer = ContentAnalyzer()
        scorer = SEOScorer(weights=custom_weights)
        llm = LLMService(api_key=api_key)

        top_keywords = kw_analyzer.extract_keywords(raw_text, top_n=15)
        target_kw_analysis = kw_analyzer.analyze_target_keyword(raw_text, target_keyword, meta_title, meta_desc, headings)
        readability = content_analyzer.analyze_readability(raw_text)
        heading_analysis = content_analyzer.analyze_heading_structure(headings)
        media_analysis = content_analyzer.analyze_media_and_links(images, links)

        score_res = scorer.calculate_score(
            word_count, target_kw_analysis, meta_title, meta_desc, heading_analysis, readability
        )

        # 3. Generators & Recommendations
        meta_gen = MetaGenerator(llm)
        kw_gen = KeywordGenerator()
        heading_gen = HeadingGenerator(llm)
        rec_engine = RecommendationEngine()
        optimizer = ContentOptimizer(llm)

        meta_recommendations = meta_gen.generate(raw_text, target_keyword or (top_keywords[0]["keyword"] if top_keywords else "SEO"))
        keyword_strategy = kw_gen.generate_keyword_strategy(raw_text, target_keyword)
        heading_outline = heading_gen.generate_recommended_outline(raw_text, target_keyword)
        rec_res = rec_engine.generate_recommendations(word_count, target_kw_analysis, meta_title, meta_desc, heading_analysis, readability, media_analysis)

        missing_lsi = keyword_strategy["missing_lsi_opportunities"]
        optimization_res = optimizer.optimize_and_compare(
            raw_text, target_keyword or keyword_strategy["primary_keyword"], missing_lsi, meta_title, meta_desc, headings
        )

        # Full Session Data Payload
        report_payload = {
            "project_name": project_name,
            "input_type": input_type,
            "user_input": user_input,
            "word_count": word_count,
            "extracted": extracted,
            "target_keyword_analysis": target_kw_analysis,
            "score": score_res,
            "top_keywords": top_keywords,
            "readability": readability,
            "heading_analysis": heading_analysis,
            "media_analysis": media_analysis,
            "meta_recommendations": meta_recommendations,
            "keyword_strategy": keyword_strategy,
            "recommended_outline": heading_outline,
            "issues_and_recommendations": rec_res,
            "optimization": optimization_res
        }

        st.session_state["active_seo_report"] = report_payload

        # Save to SQLite Database
        saved_id = db.save_analysis(
            project_name=project_name,
            input_type=input_type,
            target_keyword=target_keyword,
            seo_score=score_res["overall_score"],
            word_count=word_count,
            meta_title=meta_title,
            meta_description=meta_desc,
            search_intent=target_kw_analysis.get("intent", "Informational"),
            full_report_data=report_payload
        )
        st.success(f"Audit Complete! Saved to project database (ID #{saved_id}).")

# Display Results Dashboard if Active Report Exists
if "active_seo_report" in st.session_state:
    data = st.session_state["active_seo_report"]

    tab_overview, tab_keywords, tab_issues, tab_meta, tab_headings, tab_optimizer, tab_history, tab_export = st.tabs([
        "📊 Overview & Score",
        "🔑 Keywords & Intent",
        "⚠️ SEO Audit Issues",
        "🏷️ SERP Meta Generator",
        "🌳 Content Structure",
        "✨ AI Content Optimizer",
        "📜 Project History",
        "📥 Export Reports"
    ])

    # ---------------- TAB 1: OVERVIEW & SCORE ----------------
    with tab_overview:
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        score_val = data["score"]["overall_score"]
        
        col_s1.metric("Overall SEO Score", f"{score_val} / 100", delta=f"{score_val - 50:.1f} vs avg")
        col_s2.metric("Total Word Count", f"{data['word_count']} words")
        col_s3.metric("Flesch Readability", f"{data['readability']['flesch_reading_ease']} ({data['readability']['readability_label']})")
        col_s4.metric("Search Intent", data["target_keyword_analysis"].get("intent", "Informational"))

        st.markdown("---")
        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.subheader("🎯 Score Pillar Breakdown")
            breakdown = data["score"]["breakdown"]
            df_breakdown = pd.DataFrame({
                "Pillar": ["Metadata Quality", "Keyword Optimization", "Content Length", "Heading Structure", "Readability", "Intent Alignment"],
                "Score": [breakdown["metadata_quality"], breakdown["keyword_optimization"], breakdown["content_length"], breakdown["heading_structure"], breakdown["readability"], breakdown["intent_alignment"]]
            })
            fig_bar = px.bar(df_breakdown, x="Score", y="Pillar", orientation="h", color="Score", range_x=[0, 100], color_continuous_scale="RdYlGn")
            fig_bar.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_right:
            st.subheader("🔍 Google SERP Snippet Preview")
            curr_title = data["extracted"].get("meta_title") or "Missing Title Tag"
            curr_desc = data["extracted"].get("meta_description") or "Missing Meta Description tag. Add a description between 140-160 characters."
            curr_url = data["extracted"].get("source_url") or "https://example.com/page"

            st.markdown(f"""
            <div class="serp-card">
                <div class="serp-url">{curr_url}</div>
                <div class="serp-title">{curr_title}</div>
                <div class="serp-desc">{curr_desc}</div>
            </div>
            """, unsafe_allow_html=True)

            t_len = len(curr_title)
            d_len = len(curr_desc)
            st.caption(f"📏 Title Length: **{t_len}** chars {'✅' if 30 <= t_len <= 60 else '⚠️'} | Description Length: **{d_len}** chars {'✅' if 120 <= d_len <= 160 else '⚠️'}")

    # ---------------- TAB 2: KEYWORDS & INTENT ----------------
    with tab_keywords:
        st.subheader("🔑 Keyword Research & Search Intent Engine")
        
        target_info = data["target_keyword_analysis"]
        if target_info.get("target_keyword"):
            st.info(f"🎯 Target Keyword: **'{target_info['target_keyword']}'** | Density: **{target_info['density_pct']}%** | In Title: {'✅' if target_info['in_title'] else '❌'} | In H1: {'✅' if target_info['in_h1'] else '❌'}")

        col_k1, col_k2 = st.columns([2, 1])
        with col_k1:
            st.markdown("##### Top Extracted Term Density & TF-IDF Weights")
            if data["top_keywords"]:
                df_kw = pd.DataFrame(data["top_keywords"])
                st.dataframe(df_kw[["keyword", "count", "density_pct", "tfidf_score", "intent"]], use_container_width=True)

        with col_k2:
            st.markdown("##### Search Intent Distribution")
            intents = data["keyword_strategy"]["intent_distribution"]
            df_intent = pd.DataFrame([{"Intent": k, "Count": len(v)} for k, v in intents.items()])
            fig_pie = px.pie(df_intent, values="Count", names="Intent", title="Search Intent Breakdown", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("##### 💡 Secondary LSI Keyword Opportunities")
        missing_lsi = data["keyword_strategy"]["missing_lsi_opportunities"]
        if missing_lsi:
            st.write(", ".join([f"`{kw}`" for kw in missing_lsi]))

    # ---------------- TAB 3: SEO AUDIT ISSUES ----------------
    with tab_issues:
        st.subheader("⚠️ Categorized SEO Issues & Actionable Recommendations")
        rec_data = data["issues_and_recommendations"]

        col_i1, col_i2, col_i3 = st.columns(3)
        col_i1.error(f"🔴 Critical Issues: {rec_data['critical_count']}")
        col_i2.warning(f"🟡 Warnings: {rec_data['warning_count']}")
        col_i3.info(f"🔵 Info / Opportunities: {rec_data['info_count']}")

        st.markdown("---")
        st.markdown("#### Identified Issues Audit Log")
        for issue in rec_data["issues"]:
            sev = issue["severity"]
            badge = "badge-critical" if sev == "Critical" else ("badge-warning" if sev == "Warning" else "badge-info")
            st.markdown(f"""
            <div style="padding:10px; border-left: 4px solid {'#ef4444' if sev=='Critical' else ('#f59e0b' if sev=='Warning' else '#3b82f6')}; background-color:#f8fafc; margin-bottom:8px; border-radius:4px;">
                <span class="{badge}">{sev.upper()}</span> <b>[{issue['category']}]</b>: {issue['message']}<br/>
                <small>💡 <b>Fix:</b> {issue['solution']}</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Prioritized Fix Checklist")
        for i, rec in enumerate(rec_data["recommendations"], 1):
            st.checkbox(f"**Step {i}**: {rec}", key=f"rec_check_{i}")

    # ---------------- TAB 4: SERP META GENERATOR ----------------
    with tab_meta:
        st.subheader("🏷️ AI Meta Title & Description Generator")
        meta_rec = data["meta_recommendations"]

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### Generated Meta Title Candidates")
            for idx, item in enumerate(meta_rec["title_options"], 1):
                status_color = "green" if item["is_optimal_length"] else "orange"
                st.write(f"**Option {idx}**: {item['title']}")
                st.caption(f"Length: :{status_color}[{item['char_count']} chars ({item['status']})] | Keyword Included: {'✅' if item['has_keyword'] else '❌'}")
                st.markdown("---")

        with col_m2:
            st.markdown("#### Generated Meta Description Candidates")
            for idx, item in enumerate(meta_rec["description_options"], 1):
                status_color = "green" if item["is_optimal_length"] else "orange"
                st.write(f"**Option {idx}**: {item['description']}")
                st.caption(f"Length: :{status_color}[{item['char_count']} chars ({item['status']})] | Keyword Included: {'✅' if item['has_keyword'] else '❌'}")
                st.markdown("---")

    # ---------------- TAB 5: CONTENT STRUCTURE ----------------
    with tab_headings:
        st.subheader("🌳 Heading Hierarchy & Recommended Outline")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("#### Existing Heading Tree")
            existing_h = data["extracted"].get("headings", [])
            if existing_h:
                for h in existing_h:
                    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * (int(h['level'][1]) - 1)
                    st.markdown(f"{indent}<b>{h['level']}</b>: {h['text']}", unsafe_allow_html=True)
            else:
                st.warning("No heading tags found in extracted content.")

        with col_h2:
            st.markdown("#### Recommended SEO Structure")
            rec_outline = data["recommended_outline"]
            for h in rec_outline:
                indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * (int(h['level'][1]) - 1)
                st.markdown(f"{indent}<b>{h['level']}</b>: {h['text']}", unsafe_allow_html=True)

    # ---------------- TAB 6: AI CONTENT OPTIMIZER ----------------
    with tab_optimizer:
        st.subheader("✨ AI Content Optimizer & Comparative Metrics")
        opt = data["optimization"]
        comp = opt["comparison"]

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c1.metric("Score Delta", f"{comp['after_score']} / 100", delta=f"+{comp['score_delta']}")
        col_c2.metric("Keyword Density Delta", f"{comp['after_density']}%", delta=f"{comp['after_density'] - comp['before_density']:.2f}%")
        col_c3.metric("Readability Delta", f"{comp['after_readability']}", delta=f"{comp['after_readability'] - comp['before_readability']:.1f}")
        col_c4.metric("Word Count Change", f"{comp['after_word_count']} words", delta=f"{comp['after_word_count'] - comp['before_word_count']}")

        st.markdown("---")
        c_orig, c_opt = st.columns(2)
        with c_orig:
            st.markdown("#### Original Content")
            st.text_area("Original Text", value=opt["original_text"], height=350, disabled=True)
        with c_opt:
            st.markdown("#### AI Optimized Content")
            st.text_area("Optimized Text", value=opt["optimized_text"], height=350)

    # ---------------- TAB 7: PROJECT HISTORY ----------------
    with tab_history:
        st.subheader("📜 Saved Projects & Audit History")
        projects = db.get_all_projects()

        if projects:
            df_history = pd.DataFrame(projects)
            st.dataframe(df_history[["id", "project_name", "input_type", "target_keyword", "seo_score", "word_count", "search_intent", "created_at"]], use_container_width=True)

            selected_id = st.number_input("Enter Project ID to load or delete", min_value=1, step=1)
            col_hp1, col_hp2 = st.columns(2)
            with col_hp1:
                if st.button("📂 Load Selected Project"):
                    proj_record = db.get_project_by_id(selected_id)
                    if proj_record:
                        st.session_state["active_seo_report"] = proj_record["raw_data"]
                        st.success(f"Loaded project #{selected_id} into workspace!")
                        st.rerun()
                    else:
                        st.error("Project ID not found.")
            with col_hp2:
                if st.button("🗑️ Delete Selected Project"):
                    if db.delete_project(selected_id):
                        st.success(f"Deleted project #{selected_id}.")
                        st.rerun()
        else:
            st.info("No saved projects found in database.")

    # ---------------- TAB 8: EXPORT REPORTS ----------------
    with tab_export:
        st.subheader("📥 Export Audit Reports")
        st.write("Download executive SEO reports in PDF, Markdown, or JSON formats.")

        col_ex1, col_ex2, col_ex3 = st.columns(3)
        with col_ex1:
            pdf_bytes = exporter.generate_pdf(data)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"{data['project_name'].replace(' ', '_')}_SEO_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col_ex2:
            md_text = exporter.generate_markdown(data)
            st.download_button(
                label="📝 Download Markdown Report",
                data=md_text,
                file_name=f"{data['project_name'].replace(' ', '_')}_SEO_Report.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_ex3:
            json_text = exporter.generate_json(data)
            st.download_button(
                label="📦 Download JSON Export",
                data=json_text,
                file_name=f"{data['project_name'].replace(' ', '_')}_SEO_Report.json",
                mime="application/json",
                use_container_width=True
            )
