"""
FinSignal UI — Main entry point.
Streamlit dashboard for LinkedIn content management.
"""

import streamlit as st
import db
from pages import content_queue, comment_queue, influencer_manager

st.set_page_config(
    page_title="FinSignal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Metric cards */
    .metric-card {
        background: #1E2130;
        border-radius: 10px;
        padding: 20px 24px;
        border-left: 4px solid #0A66C2;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #9AA0B2;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FAFAFA;
        line-height: 1;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #9AA0B2;
        margin-top: 4px;
    }

    /* Page header */
    .page-header {
        margin-bottom: 24px;
    }
    .page-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FAFAFA;
    }
    .page-subtitle {
        font-size: 0.9rem;
        color: #9AA0B2;
        margin-top: 2px;
    }

    /* Tab styling */
    div[data-testid="stTabs"] button {
        font-size: 0.92rem;
        font-weight: 600;
    }

    /* Divider */
    hr { border-color: #2C3045; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Init DB ────────────────────────────────────────────────────────────────────
db.ensure_tables()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <div class="page-title">📊 FinSignal</div>
        <div class="page-subtitle">LinkedIn Content Intelligence for Financial Crime Compliance</div>
    </div>
    <hr/>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br/>", unsafe_allow_html=True)

# ── Metrics row ────────────────────────────────────────────────────────────────
metrics = db.get_metrics()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Posts This Week</div>
            <div class="metric-value">{metrics['posts_this_week']}</div>
            <div class="metric-sub">content queue items created</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Drafts Pending</div>
            <div class="metric-value">{metrics['draft_count']}</div>
            <div class="metric-sub">awaiting review &amp; approval</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Comments Queued</div>
            <div class="metric-value">{metrics['pending_comments']}</div>
            <div class="metric-sub">pending posts</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Warm Connections</div>
            <div class="metric-value">{metrics['warm_influencers']}</div>
            <div class="metric-sub">influencers engaged</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<br/>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📝  Content Queue", "💬  Comment Queue", "🤝  Influencer Manager"]
)

with tab1:
    content_queue.render()

with tab2:
    comment_queue.render()

with tab3:
    influencer_manager.render()
