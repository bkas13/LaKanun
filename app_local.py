#!/usr/bin/env python3
"""
ल Kanun — Self-contained app with full corpus loaded directly.
Run: streamlit run app_local.py --server.port 3030
"""

import json
from pathlib import Path
from typing import Dict, List

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ल Kanun",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Data Loading
# ============================================================================

@st.cache_data
def load_nepal_constitution() -> Dict:
    path = Path(__file__).parent / "data" / "processed" / "nepal_constitution.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_india_laws() -> Dict:
    path = Path(__file__).parent / "data" / "processed" / "india_laws.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_articles(articles: List[Dict], query: str, country: str = None,
                    category: str = None, top_k: int = 10) -> List[Dict]:
    query_lower = query.lower()
    query_words = set(query_lower.split())
    results = []
    for art in articles:
        if country and art.get("country") != country:
            continue
        if category and category != "all" and art.get("category") != category:
            continue
        text_lower = (art.get("full_text", "") + " " + art.get("title", "")).lower()
        score = sum(1 for w in query_words if w in text_lower)
        if query_lower in text_lower:
            score += 5
        if query_lower in art.get("title", "").lower():
            score += 3
        if score > 0:
            results.append({"article": art, "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def get_category_stats(articles: List[Dict]) -> Dict[str, int]:
    stats = {}
    for art in articles:
        cat = art.get("category", "unknown")
        stats[cat] = stats.get(cat, 0) + 1
    return stats

# ============================================================================
# Custom CSS
# ============================================================================

st.markdown("""
<style>
    /* ===== Base ===== */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* ===== Cards ===== */
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        text-align: center;
        border: 1px solid #E5E7EB;
    }
    .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-top: 0.2rem;
    }

    /* ===== Article Cards ===== */
    .article-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin: 0.4rem 0;
        background: white;
        border-left: 3px solid #D1D5DB;
    }

    /* ===== Badges ===== */
    .category-badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 500;
        margin-right: 0.25rem;
        background: #F3F4F6;
        color: #374151;
    }

    /* ===== Disclaimer ===== */
    .disclaimer {
        font-size: 0.8rem;
        color: #9CA3AF;
        font-style: italic;
        padding: 0.5rem;
        background: #F9FAFB;
        border-radius: 6px;
        margin-top: 0.75rem;
    }

    /* ===== Part Headers ===== */
    .part-header {
        background: #F3F4F6;
        padding: 0.5rem 0.85rem;
        border-radius: 6px;
        margin: 0.6rem 0 0.4rem 0;
        font-weight: 600;
        color: #1F2937;
        font-size: 0.9rem;
        border: 1px solid #E5E7EB;
    }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: #6B7280;
    }
    .stTabs [aria-selected="true"] {
        font-weight: 600;
        color: #111827;
    }

    /* ===== Buttons ===== */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: #1F2937 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4 {
        color: #F9FAFB !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #374151 !important;
    }
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        color: #F9FAFB !important;
    }
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] {
        background-color: #374151;
        border-color: #4B5563;
        color: #E5E7EB;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] span {
        color: #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Load Data
# ============================================================================

nepal_data = load_nepal_constitution()
india_data = load_india_laws()
ALL_ARTICLES = nepal_data["articles"] + india_data["articles"]

CAT_COLORS = {
    "fundamental_rights": "#28A745",
    "directive_principles": "#17A2B8",
    "executive": "#6F42C1",
    "legislature": "#FD7E14",
    "judiciary": "#DC3545",
    "constitutional_bodies": "#E83E8C",
    "local_government": "#20C997",
    "federal_finance": "#FFC107",
    "intergovernmental_relations": "#6610F2",
    "civil_service": "#0DCAF0",
    "election_commission": "#D63384",
    "audit_finance": "#FF8502",
    "commissions": "#0D6EFD",
    "political_parties": "#198754",
    "emergency_powers": "#DC3545",
    "miscellaneous": "#6C757D",
    "transitional_provisions": "#ADB5BD",
    "constitutional": "#0D6EFD",
    "criminal": "#DC3545",
    "civil": "#0D6EFD",
    "labor": "#FFC107",
    "penal_code": "#DC3545",
    "procedure_code": "#FD7E14",
    "act": "#6F42C1",
}

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.markdown("## ⚖️ ल Kanun")
    st.markdown("---")

    st.markdown("### 📊 Corpus Statistics")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Nepal", f"{nepal_data['total_articles']}", "articles")
    with c2:
        st.metric("India", f"{india_data['total_articles']}", "articles")
    st.metric("Total", f"{len(ALL_ARTICLES)}", "legal provisions")

    st.markdown("---")
    country_filter = st.selectbox(
        "🌍 Filter by Country",
        ["all", "nepal", "india"],
        format_func=lambda x: {"all": "All Countries", "nepal": "🇳🇵 Nepal", "india": "🇮🇳 India"}[x],
    )

    all_categories = sorted(set(a.get("category", "") for a in ALL_ARTICLES))
    category_filter = st.selectbox(
        "📁 Filter by Category",
        ["all"] + all_categories,
        format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Categories",
    )

    all_doc_types = sorted(set(a.get("document_type", "") for a in ALL_ARTICLES))
    doc_type_filter = st.selectbox(
        "📄 Document Type",
        ["all"] + all_doc_types,
        format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Types",
    )

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
    ⚠️ <strong>Disclaimer:</strong> AI-generated legal information.
    Not professional legal advice. Consult a qualified attorney.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# Main Content
# ============================================================================

st.markdown('<h1 class="main-header">⚖️ ल Kanun</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Complete Legal Corpus: Nepal Constitution 2072 & Indian Laws</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Search", "📖 Nepal Constitution", "📜 Indian Laws",
    "📊 Analytics", "ℹ️ About"
])

# ============================================================================
# Tab 1: Search
# ============================================================================

with tab1:
    st.markdown("### 🔍 Search Legal Corpus")

    search_query = st.text_input(
        "Search query",
        placeholder="e.g., 'right to equality', 'murder punishment', 'warrant arrest'",
        key="search_input",
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_top_k = st.slider("Max results", 5, 50, 15, key="search_top_k")
    with col2:
        search_country = st.selectbox("Country", ["all", "nepal", "india"],
                                       format_func=lambda x: {"all": "All", "nepal": "Nepal", "india": "India"}[x],
                                       key="search_country")
    with col3:
        search_cat = st.selectbox("Category", ["all"] + all_categories,
                                   format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All",
                                   key="search_cat")

    if st.button("🔍 Search", type="primary", use_container_width=True) and search_query:
        with st.spinner("Searching..."):
            results = search_articles(ALL_ARTICLES, search_query,
                                       country=search_country if search_country != "all" else None,
                                       category=search_cat if search_cat != "all" else None,
                                       top_k=search_top_k)

        if results:
            st.markdown(f'**Found {len(results)} results** for "{search_query}"')

            for i, res in enumerate(results):
                art = res["article"]
                score = res["score"]
                cat = art.get("category", "unknown")
                color = CAT_COLORS.get(cat, "#6C757D")

                with st.expander(
                    f"**{i+1}.** {art.get('title', 'Untitled')} — "
                    f"`{art.get('country', '').upper()}` • {cat.replace('_', ' ').title()} "
                    f"(relevance: {score})"
                ):
                    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                    with mcol1:
                        st.markdown(f"**Country:** {art.get('country', '').upper()}")
                    with mcol2:
                        st.markdown(f"**Category:** `{cat}`")
                    with mcol3:
                        st.markdown(f"**Article:** {art.get('article_number', 'N/A')}")
                    with mcol4:
                        st.markdown(f"**Type:** {art.get('document_type', '').replace('_', ' ').title()}")

                    if art.get("part"):
                        st.markdown(f"**Part:** {art['part']}")

                    st.markdown("---")
                    st.text(art.get("full_text", "No text available.")[:2000])

                    refs = art.get("cross_references", [])
                    if refs:
                        st.markdown(f"**Cross-references:** {', '.join(refs[:10])}")
        else:
            st.info("No results found. Try different keywords.")

# ============================================================================
# Tab 2: Nepal Constitution
# ============================================================================

with tab2:
    st.markdown("### 🇳🇵 Constitution of Nepal 2072")
    st.markdown(f"**{nepal_data['total_articles']} articles** across **35 Parts** and **9 Schedules**")

    with st.expander("📋 Schedules (9)"):
        for sched_num, sched_title in nepal_data.get("schedules", {}).items():
            st.markdown(f"**Schedule {sched_num}:** {sched_title}")

    articles_by_part = {}
    for art in nepal_data["articles"]:
        part = art.get("part", "Unknown")
        if part not in articles_by_part:
            articles_by_part[part] = []
        articles_by_part[part].append(art)

    nepal_cats = sorted(set(a.get("category", "") for a in nepal_data["articles"]))
    nepal_cat_filter = st.selectbox(
        "Filter by category",
        ["all"] + nepal_cats,
        format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Categories",
        key="nepal_cat_filter",
    )

    for part_name in sorted(articles_by_part.keys()):
        part_articles = articles_by_part[part_name]

        if nepal_cat_filter != "all":
            part_articles = [a for a in part_articles if a.get("category") == nepal_cat_filter]
            if not part_articles:
                continue

        st.markdown(f'<div class="part-header">{part_name} ({len(part_articles)} articles)</div>',
                     unsafe_allow_html=True)

        for art in part_articles[:5]:
            cat = art.get("category", "")
            color = CAT_COLORS.get(cat, "#6C757D")
            st.markdown(
                f"""<div class="article-card">
                <span class="category-badge" style="background: {color}20; color: {color};">{cat.replace('_', ' ').title()}</span>
                <strong>Art. {art['article_number']}</strong>: {art.get('title', 'Untitled')}
                </div>""",
                unsafe_allow_html=True,
            )
            with st.expander(f"View Art. {art['article_number']}", expanded=False):
                st.text(art.get("full_text", ""))

        if len(part_articles) > 5:
            st.caption(f"... and {len(part_articles) - 5} more articles in this part")

# ============================================================================
# Tab 3: Indian Laws
# ============================================================================

with tab3:
    st.markdown("### 🇮🇳 Indian Legal Documents")
    st.markdown(f"**{india_data['total_articles']} provisions** across 6 documents")

    doc_stats = {}
    for art in india_data["articles"]:
        dt = art.get("document_type", "unknown")
        doc_stats[dt] = doc_stats.get(dt, 0) + 1

    cols = st.columns(3)
    for i, (dt, count) in enumerate(doc_stats.items()):
        with cols[i % 3]:
            st.metric(dt.replace("_", " ").title(), f"{count}")

    doc_names = sorted(set(a.get("source_document", "") for a in india_data["articles"]))
    selected_doc = st.selectbox(
        "Select Document",
        ["all"] + doc_names,
        format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Documents",
        key="india_doc_filter",
    )

    india_cats = sorted(set(a.get("category", "") for a in india_data["articles"]))
    india_cat_filter = st.selectbox(
        "Filter by category",
        ["all"] + india_cats,
        format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Categories",
        key="india_cat_filter",
    )

    filtered_india = india_data["articles"]
    if selected_doc != "all":
        filtered_india = [a for a in filtered_india if a.get("source_document") == selected_doc]
    if india_cat_filter != "all":
        filtered_india = [a for a in filtered_india if a.get("category") == india_cat_filter]

    st.markdown(f"**Showing {len(filtered_india)} provisions**")

    for art in filtered_india[:20]:
        cat = art.get("category", "")
        color = CAT_COLORS.get(cat, "#6C757D")
        with st.expander(
            f"**{art.get('source_document', '').replace('_', ' ').title()}** — "
            f"Art/Sec {art.get('article_number', 'N/A')}: {art.get('title', '')[:60]}"
        ):
            st.markdown(
                f"""<span class="category-badge" style="background: {color}20; color: {color};">
                {cat.replace('_', ' ').title()}</span>""",
                unsafe_allow_html=True,
            )
            st.text(art.get("full_text", "")[:1500])

# ============================================================================
# Tab 4: Analytics
# ============================================================================

with tab4:
    st.markdown("### 📊 Corpus Analytics")

    col1, col2 = st.columns(2)

    with col1:
        nepal_cat_stats = get_category_stats(nepal_data["articles"])
        fig_nepal = px.pie(
            names=list(nepal_cat_stats.keys()),
            values=list(nepal_cat_stats.values()),
            title="Nepal Constitution - Categories",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_nepal.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_nepal, use_container_width=True)

    with col2:
        india_cat_stats = get_category_stats(india_data["articles"])
        fig_india = px.pie(
            names=list(india_cat_stats.keys()),
            values=list(india_cat_stats.values()),
            title="Indian Laws - Categories",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_india.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_india, use_container_width=True)

    st.markdown("#### 📊 Category Distribution Comparison")
    all_cats = sorted(set(list(nepal_cat_stats.keys()) + list(india_cat_stats.keys())))
    comparison_data = []
    for cat in all_cats:
        comparison_data.append({
            "Category": cat.replace("_", " ").title(),
            "Nepal": nepal_cat_stats.get(cat, 0),
            "India": india_cat_stats.get(cat, 0),
        })

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Nepal", x=[d["Category"] for d in comparison_data],
        y=[d["Nepal"] for d in comparison_data], marker_color="#28A745",
    ))
    fig_bar.add_trace(go.Bar(
        name="India", x=[d["Category"] for d in comparison_data],
        y=[d["India"] for d in comparison_data], marker_color="#0D6EFD",
    ))
    fig_bar.update_layout(barmode="group", height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 🇮🇳 Indian Documents Breakdown")
    doc_type_stats = {}
    for art in india_data["articles"]:
        dt = art.get("document_type", "unknown")
        doc_type_stats[dt] = doc_type_stats.get(dt, 0) + 1

    fig_docs = px.bar(
        x=list(doc_type_stats.keys()),
        y=list(doc_type_stats.values()),
        title="Indian Laws by Document Type",
        labels={"x": "Document Type", "y": "Count"},
        color=list(doc_type_stats.keys()),
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    st.plotly_chart(fig_docs, use_container_width=True)

    st.markdown("#### 🌏 Country Comparison")
    comp_cols = st.columns(2)
    with comp_cols[0]:
        st.metric("Nepal Constitution", f"{nepal_data['total_articles']}", "articles")
    with comp_cols[1]:
        st.metric("Indian Laws", f"{india_data['total_articles']}", "provisions")

# ============================================================================
# Tab 5: About
# ============================================================================

with tab5:
    st.markdown("### ℹ️ About ल Kanun")

    st.markdown("""
    **ल Kanun** is a comprehensive legal information system covering:

    #### 🇳🇵 Nepal Constitution 2072
    - **308 Articles** across **35 Parts**
    - **9 Schedules** (Federal, Provincial, Local subjects; National symbols)
    - Categories: Fundamental Rights, Directive Principles, Executive, Legislature,
      Judiciary, Constitutional Bodies, Local Government, Federal Finance, and more

    #### 🇮🇳 Indian Legal Documents
    - **Constitution of India** (453 articles)
    - **Indian Penal Code, 1860** (511 sections)
    - **Code of Criminal Procedure, 1973** (484 sections)
    - **Code of Civil Procedure, 1908** (158 sections)
    - **Indian Contract Act, 1872** (266 sections)
    - **Minimum Wages Act, 1948** (32 sections)

    #### 📊 Total Corpus
    - **2,212 legal provisions** across both countries
    - Unified JSON schema for consistent processing
    - Cross-referenced articles
    - Category-based organization

    #### ⚙️ Technical Details
    - Data stored in `data/processed/nepal_constitution.json` and `data/processed/india_laws.json`
    - Ingested via `data/ingest_constitution.py`
    - Supports multilingual search (English, Nepali, Hindi)
    """)

    st.markdown("---")
    st.markdown("""
    <div class="disclaimer">
    ⚠️ <strong>Disclaimer:</strong> This system provides AI-generated legal information
    for educational purposes only. It is NOT a substitute for professional legal advice.
    Always consult a qualified attorney for legal matters.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #6C757D; font-size: 0.8rem;">'
    'ल Kanun • Nepal Constitution 2072 & Indian Laws • Powered by AI</p>',
    unsafe_allow_html=True,
)
