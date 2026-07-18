"""
Streamlit Web UI for Nepal Legal AI.
Multilingual legal analysis interface for Nepal and India.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit.components.v1 import html

# Page config
st.set_page_config(
    page_title="Nepal Legal AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1B3A5C;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .classification-legal { background-color: #D4EDDA; color: #155724; padding: 1rem; border-radius: 0.5rem; font-weight: bold; }
    .classification-illegal { background-color: #F8D7DA; color: #721C24; padding: 1rem; border-radius: 0.5rem; font-weight: bold; }
    .classification-conditional { background-color: #FFF3CD; color: #856404; padding: 1rem; border-radius: 0.5rem; font-weight: bold; }
    .classification-gray { background-color: #E2E3E5; color: #383D41; padding: 1rem; border-radius: 0.5rem; font-weight: bold; }
    .confidence-bar { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #DC3545 0%, #FFC107 50%, #28A745 100%); }
    .law-card { border: 1px solid #DEE2E6; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0; background: #FAFAFA; }
    .stance-violates { color: #DC3545; font-weight: bold; }
    .stance-supports { color: #28A745; font-weight: bold; }
    .stance-conditional { color: #FFC107; font-weight: bold; }
    .stance-related { color: #007BFF; font-weight: bold; }
    .disclaimer { font-size: 0.85rem; color: #6C757D; font-style: italic; margin-top: 1rem; padding: 0.5rem; background: #F8F9FA; border-radius: 0.25rem; }
    .stat-card { background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #1B3A5C; }
    .stat-label { font-size: 0.9rem; color: #6C757D; }
    .sidebar-header { font-size: 1.2rem; font-weight: 600; color: #1B3A5C; margin-bottom: 1rem; }
    .sample-button { width: 100%; text-align: left; margin: 0.25rem 0; padding: 0.5rem; background: #F8F9FA; border: 1px solid #DEE2E6; border-radius: 0.25rem; }
    .sample-button:hover { background: #E9ECEF; cursor: pointer; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000"

SAMPLE_SCENARIOS_NEPAL = [
    "Can my employer fire me without any notice?",
    "Is caste discrimination punishable in Nepal?",
    "Can police arrest me without a warrant?",
    "What are my rights if I'm detained?",
    "Can I start a business without registration?",
    "Is dowry legal in Nepal?",
    "What are the laws on child marriage?",
    "Can a woman inherit parental property equally?",
    "Is forced labor legal in Nepal?",
    "Can the government acquire my land without compensation?",
    "What are my rights as a consumer in Nepal?",
    "Is it legal to convert someone's religion by force?",
]

SAMPLE_SCENARIOS_INDIA = [
    "Can police arrest me without a warrant for a minor offense?",
    "Is triple talaq legal in India?",
    "Can my employer withhold my salary?",
    "What are my rights if I'm arrested?",
    "Is it legal to discriminate based on caste in hiring?",
    "Can I be forced to work overtime without pay?",
    "What is the legal age of marriage in India?",
    "Can a woman inherit ancestral property equally?",
    "Is marital rape criminalized in India?",
    "Can the government acquire my land for public purpose?",
    "What are my rights as a consumer in India?",
    "Is it legal to convert someone's religion by inducement?",
]

CLASSIFICATION_COLORS = {
    "legal": "#28A745",
    "illegal": "#DC3545",
    "illegal_with_conditions": "#FFC107",
    "partially_legal": "#17A2B8",
    "requires_permits": "#6F42C1",
    "gray_area": "#6C757D",
    "jurisdiction_specific": "#FD7E14",
}

STANCE_COLORS = {
    "violates": "#DC3545",
    "supports": "#28A745",
    "conditional": "#FFC107",
    "related": "#007BFF",
    "neutral": "#6C757D",
}

SEVERITY_COLORS = {
    "low": "#28A745",
    "medium": "#FFC107",
    "high": "#FD7E14",
    "critical": "#DC3545",
}


# ============================================================================
# Session State Initialization
# ============================================================================

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = {}


# ============================================================================
# API Helper Functions
# ============================================================================

def api_analyze(query: str, country: str, language: str, top_k: int = 10) -> Optional[Dict]:
    """Call the analyze API endpoint."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"query": query, "country": country, "language": language, "top_k": top_k},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API server. Please ensure the API is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def api_search(query: str, country: Optional[str], category: Optional[str], top_k: int) -> Optional[Dict]:
    """Call the search API endpoint."""
    try:
        params = {"q": query, "top_k": top_k}
        if country:
            params["country"] = country
        if category:
            params["category"] = category

        response = requests.get(f"{API_BASE_URL}/search", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return None


def api_health() -> Optional[Dict]:
    """Check API health."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def api_dictionary_search(query: str, lang: str) -> Optional[Dict]:
    """Search legal dictionary."""
    try:
        response = requests.get(f"{API_BASE_URL}/dictionary/search", params={"q": query, "lang": lang}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def api_get_article(article_id: str) -> Optional[Dict]:
    """Get article by ID."""
    try:
        response = requests.get(f"{API_BASE_URL}/article/{article_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def submit_feedback(query_id: str, rating: int, correction: str = "", comments: str = "") -> bool:
    """Submit user feedback."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback",
            json={"query_id": query_id, "rating": rating, "correction": correction, "comments": comments},
            timeout=10,
        )
        return response.status_code == 200
    except Exception:
        return False


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">⚖️ Nepal Legal AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Multilingual Legal Analysis for Nepal & India • Powered by AI</p>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the sidebar with controls and stats."""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🎛️ Controls</div>', unsafe_allow_html=True)

        # Country selector
        country = st.selectbox(
            "Country / देश / देश",
            ["nepal", "india"],
            format_func=lambda x: {"nepal": "🇳🇵 Nepal", "india": "🇮🇳 India"}[x],
            key="country_selector",
        )

        # Language selector
        language = st.selectbox(
            "Language / भाषा / भाषा",
            ["en", "ne", "hi"],
            format_func=lambda x: {"en": "🇬🇧 English", "ne": "🇳🇵 नेपाली", "hi": "🇮🇳 हिन्दी"}[x],
            key="language_selector",
        )

        # API Status
        st.markdown("---")
        st.markdown('<div class="sidebar-header">📊 System Status</div>', unsafe_allow_html=True)

        health = api_health()
        if health:
            st.success("✅ API Connected")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Corpus Size", f"{health.get('corpus_size', 0):,}")
            with col2:
                st.metric("Countries", len(health.get('countries', [])))
        else:
            st.error("❌ API Disconnected")
            st.caption("Start the API server: `python -m src.api`")

        # Statistics
        if st.session_state.analysis_history:
            st.markdown("---")
            st.markdown('<div class="sidebar-header">📈 Session Stats</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Queries", len(st.session_state.analysis_history))
            with col2:
                avg_conf = sum(a.get("confidence", 0) for a in st.session_state.analysis_history) / len(st.session_state.analysis_history)
                st.metric("Avg Confidence", f"{avg_conf:.0%}")

        # Clear history
        if st.session_state.analysis_history:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.analysis_history = []
                st.session_state.current_analysis = None
                st.rerun()

        # About
        st.markdown("---")
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Nepal Legal AI** provides AI-powered legal analysis for Nepal and India.

            **Features:**
            - Multilingual (English, Nepali, Hindi)
            - Constitutional & statutory law coverage
            - Citation-backed reasoning
            - Legal remedy suggestions

            **Disclaimer:** This is AI-generated analysis, not professional legal advice. Consult a qualified attorney for legal matters.
            """)

        return country, language


def render_classification_badge(classification: str, confidence: float):
    """Render classification with color coding."""
    color = CLASSIFICATION_COLORS.get(classification, "#6C757D")
    label = classification.replace("_", " ").title()

    st.markdown(
        f"""
        <div style="
            background-color: {color}20;
            border-left: 4px solid {color};
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        ">
            <span style="color: {color}; font-weight: 700; font-size: 1.2rem;">{label}</span>
            <span style="margin-left: 1rem; color: #6C757D;">Confidence: {confidence:.0%}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_confidence_bar(confidence: float):
    """Render a confidence progress bar."""
    color = "#28A745" if confidence > 0.7 else "#FFC107" if confidence > 0.4 else "#DC3545"
    st.markdown(
        f"""
        <div style="margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span>Confidence</span>
                <span style="color: {color}; font-weight: bold;">{confidence:.0%}</span>
            </div>
            <div style="height: 8px; border-radius: 4px; background: #E9ECEF;">
                <div style="
                    width: {confidence * 100}%;
                    height: 100%;
                    border-radius: 4px;
                    background: {color};
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_result(analysis: Dict):
    """Render the complete analysis result."""
    # Classification badge
    render_classification_badge(analysis["classification"], analysis["confidence"])

    # Confidence bar
    render_confidence_bar(analysis["confidence"])

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        severity = analysis.get("severity", "medium")
        color = SEVERITY_COLORS.get(severity, "#6C757D")
        st.markdown(
            f'<div class="stat-card"><div class="stat-value" style="color: {color};">{severity.upper()}</div><div class="stat-label">Severity</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        domains = analysis.get("legal_domains", [])
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{len(domains)}</div><div class="stat-label">Legal Domains</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        laws_count = len(analysis.get("applicable_laws", []))
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{laws_count}</div><div class="stat-label">Applicable Laws</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        jurisdiction = analysis.get("jurisdiction", "").upper()
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{jurisdiction}</div><div class="stat-label">Jurisdiction</div></div>',
            unsafe_allow_html=True,
        )

    # Legal domains
    if domains:
        st.markdown("**Legal Domains:** " + ", ".join([f"`{d}`" for d in domains]))

    # Reasoning
    with st.expander("🧠 Legal Reasoning", expanded=True):
        st.markdown(analysis.get("reasoning", "No reasoning provided."))

    # Applicable Laws
    laws = analysis.get("applicable_laws", [])
    if laws:
        st.markdown("### ⚖️ Applicable Laws")
        for i, law in enumerate(laws, 1):
            stance = law.get("stance", "related")
            stance_color = STANCE_COLORS.get(stance, "#6C757D")
            stance_label = stance.upper()

            with st.container():
                st.markdown(
                    f"""
                    <div class="law-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>{i}. {law.get('title', 'Unknown Law')}</strong>
                            <span style="color: {stance_color}; font-weight: 600; background: {stance_color}20; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.8rem;">
                                {stance_label}
                            </span>
                        </div>
                        <div style="color: #6C757D; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            {law.get('country', '').upper()} • {law.get('category', '').replace('_', ' ').title()} • Article/Section: {law.get('article_number', 'N/A')}
                        </div>
                        <div style="font-size: 0.85rem; color: #495057; margin-bottom: 0.5rem;">
                            {law.get('explanation', '')[:300]}{'...' if len(law.get('explanation', '')) > 300 else ''}
                        </div>
                        <details style="font-size: 0.8rem;">
                            <summary style="color: #007BFF; cursor: pointer;">View Full Text</summary>
                            <pre style="background: #F8F9FA; padding: 0.5rem; border-radius: 0.25rem; overflow-x: auto; margin-top: 0.5rem;">{law.get('text', '')[:1000]}</pre>
                        </details>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Recommended Action
    if analysis.get("recommended_action"):
        st.markdown("### 💡 Recommended Action")
        st.info(analysis["recommended_action"])

    # Disclaimer
    st.markdown(
        f'<div class="disclaimer">⚠️ {analysis.get("disclaimer", "This is AI-generated analysis, not professional legal advice. Consult a qualified attorney.")}</div>',
        unsafe_allow_html=True,
    )

    # Feedback
    render_feedback_widget(analysis)


def render_feedback_widget(analysis: Dict):
    """Render feedback widget for the analysis."""
    query_id = analysis.get("query_id", "")

    if query_id in st.session_state.feedback_submitted:
        st.success("✅ Thank you for your feedback!")
        return

    st.markdown("### 📝 Was this analysis helpful?")
    col1, col2, col3, col4, col5 = st.columns(5)

    for i, col in enumerate([col1, col2, col3, col4, col5], 1):
        with col:
            if st.button(f"{i}⭐", key=f"feedback_{query_id}_{i}", use_container_width=True):
                correction = st.session_state.get(f"correction_{query_id}", "")
                comments = st.session_state.get(f"comments_{query_id}", "")
                if submit_feedback(query_id, i, correction, comments):
                    st.session_state.feedback_submitted[query_id] = True
                    st.success("Feedback submitted!")
                    st.rerun()

    with st.expander("Provide detailed feedback"):
        correction = st.text_area("Correction (if any)", key=f"correction_{query_id}")
        comments = st.text_area("Additional comments", key=f"comments_{query_id}")


def render_sample_scenarios(country: str):
    """Render sample scenario buttons."""
    scenarios = SAMPLE_SCENARIOS_NEPAL if country == "nepal" else SAMPLE_SCENARIOS_INDIA

    st.markdown("**💡 Try a sample scenario:**")
    cols = st.columns(2)
    for i, scenario in enumerate(scenarios):
        col = cols[i % 2]
        with col:
            if st.button(scenario, key=f"sample_{i}", use_container_width=True):
                st.session_state.sample_query = scenario
                st.rerun()


def render_search_tab(country: str):
    """Render the legal corpus search tab."""
    st.markdown("### 🔍 Search Legal Corpus")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search query", placeholder="e.g., 'right to equality', 'labor law notice period'")
    with col2:
        category = st.selectbox(
            "Category",
            ["All"] + ["fundamental_rights", "criminal", "civil", "labor", "family", "property", "constitutional"],
            format_func=lambda x: x.replace("_", " ").title() if x != "All" else "All Categories",
        )

    top_k = st.slider("Results", 1, 20, 10)

    if st.button("🔍 Search", type="primary") and search_query:
        with st.spinner("Searching..."):
            results = api_search(search_query, country if country != "All" else None, category if category != "All" else None, top_k)

        if results and results.get("results"):
            st.markdown(f"**Found {results['total']} results**")
            for i, result in enumerate(results["results"], 1):
                meta = result["metadata"]
                with st.expander(f"{i}. {meta.get('title', 'Unknown')} (Score: {result['score']:.2%})"):
                    st.markdown(f"**Country:** {meta.get('country', '').upper()}")
                    st.markdown(f"**Category:** {meta.get('category', '').replace('_', ' ').title()}")
                    st.markdown(f"**Article/Section:** {meta.get('article_number', 'N/A')}")
                    st.markdown(f"**Relevance:** {result['score']:.2%}")
                    st.markdown("---")
                    st.text(result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"])
        else:
            st.info("No results found. Try a different query.")


def render_dictionary_tab(language: str):
    """Render the legal dictionary tab."""
    st.markdown("### 📚 Legal Dictionary")

    lang_map = {"en": "English", "ne": "नेपाली (Nepali)", "hi": "हिन्दी (Hindi)"}
    target_lang = st.selectbox("Target Language", ["ne", "hi"], format_func=lambda x: lang_map[x])

    query = st.text_input("Search legal term", placeholder="e.g., bail, warrant, inheritance, divorce")

    if query:
        with st.spinner("Searching..."):
            results = api_dictionary_search(query, target_lang)

        if results and results.get("results"):
            for result in results["results"]:
                with st.expander(f"{result.get('english', '')} → {result.get(target_lang, '')}"):
                    st.markdown(f"**English:** {result.get('english', '')}")
                    st.markdown(f"**{lang_map[target_lang]}:** {result.get(target_lang, '')}")
                    if result.get("definition"):
                        st.markdown(f"**Definition:** {result['definition']}")
                    if result.get("context"):
                        st.markdown(f"**Context:** {result['context']}")
        else:
            st.info("No translation found. Try a different term.")


def render_history_tab():
    """Render analysis history."""
    st.markdown("### 📜 Analysis History")

    if not st.session_state.analysis_history:
        st.info("No analyses yet. Submit a query to see history.")
        return

    for i, analysis in enumerate(reversed(st.session_state.analysis_history)):
        query_id = analysis.get("query_id", "")
        with st.expander(f"{analysis.get('query', '')[:80]}... ({analysis.get('classification', '')})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Query:** {analysis.get('query', '')}")
                st.markdown(f"**Classification:** {analysis.get('classification', '').replace('_', ' ').title()}")
                st.markdown(f"**Confidence:** {analysis.get('confidence', 0):.0%}")
            with col2:
                st.markdown(f"**Country:** {analysis.get('jurisdiction', '').upper()}")
                st.markdown(f"**Time:** {analysis.get('timestamp', '')[:19]}")

            if st.button("View Full Analysis", key=f"history_view_{i}"):
                st.session_state.current_analysis = analysis
                st.rerun()


def render_main_interface(country: str, language: str):
    """Render the main analysis interface."""
    # Sample scenarios
    render_sample_scenarios(country)

    # Query input
    default_query = st.session_state.get("sample_query", "")
    if default_query:
        del st.session_state.sample_query

    query = st.text_area(
        "Describe your legal scenario or ask a legal question:",
        value=default_query,
        height=120,
        placeholder=(
            "Examples:\n"
            "• Can my employer fire me without notice?\n"
            "• Is caste discrimination punishable?\n"
            "• Can police arrest me without a warrant?\n"
            "• What are my rights if I'm detained?"
        ),
    )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        top_k = st.slider("Number of laws to retrieve", 5, 20, 10)
        use_llm = st.checkbox("Use LLM for reasoning (requires API key)", value=True)

    # Analyze button
    if st.button("🔍 Analyze", type="primary", use_container_width=True, disabled=not query.strip()):
        with st.spinner("Analyzing legal scenario..."):
            analysis = api_analyze(query, country, language, top_k)

        if analysis:
            st.session_state.current_analysis = analysis
            # Add to history (avoid duplicates)
            if not any(a.get("query_id") == analysis.get("query_id") for a in st.session_state.analysis_history):
                st.session_state.analysis_history.append(analysis)
            st.rerun()

    # Display current analysis
    if st.session_state.current_analysis:
        st.markdown("---")
        render_analysis_result(st.session_state.current_analysis)


def main():
    """Main Streamlit app."""
    render_header()

    # Sidebar
    country, language = render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Analyze", "📖 Search Laws", "📚 Dictionary", "📜 History"])

    with tab1:
        render_main_interface(country, language)

    with tab2:
        render_search_tab(country)

    with tab3:
        render_dictionary_tab(language)

    with tab4:
        render_history_tab()


if __name__ == "__main__":
    main()