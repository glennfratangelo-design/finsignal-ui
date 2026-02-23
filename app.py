"""
FinSignal UI — Main entry point.
Streamlit dashboard for LinkedIn content management.
"""

import os
from datetime import datetime, timedelta, timezone

import streamlit as st
import db
from pages import content_queue, comment_queue, influencer_manager

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="FinSignal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Hide default Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

    /* ── Metric cards ── */
    .metric-card {
        background: #1E2130;
        border-radius: 8px;
        padding: 18px 20px;
        border: 1px solid #2D3748;
        transition: border-color 0.2s ease;
        cursor: pointer;
        min-height: 96px;
    }
    .metric-card:hover { border-color: #0A66C2; }
    .metric-card.active { border-left: 3px solid #0A66C2; }
    .metric-label {
        font-size: 0.74rem;
        color: #9AA0B2;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #FAFAFA;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.73rem;
        color: #6B7280;
        margin-top: 3px;
    }

    /* ── Nav tab buttons ── */
    .tab-nav button {
        background: #1E2130 !important;
        border: 1px solid #2D3748 !important;
        border-radius: 8px !important;
        color: #9AA0B2 !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.15s ease !important;
    }
    .tab-nav button:hover {
        border-color: #0A66C2 !important;
        color: #FAFAFA !important;
    }

    /* ── All st.button rounded corners ── */
    button[kind="secondary"], button[kind="primary"] {
        border-radius: 6px !important;
    }

    /* ── LinkedIn connect banner ── */
    .li-banner {
        background: #1A1C2A;
        border: 1px solid #F5A623;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .li-banner-text {
        font-size: 0.88rem;
        color: #F5A623;
        flex: 1;
    }

    /* ── Profile chip ── */
    .profile-chip {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #1E2130;
        border: 1px solid #2D3748;
        border-radius: 40px;
        padding: 6px 14px 6px 6px;
        float: right;
    }
    .profile-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
    }
    .profile-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: #FAFAFA;
    }
    .profile-title {
        font-size: 0.72rem;
        color: #9AA0B2;
    }

    /* ── Divider ── */
    hr { border-color: #2D3748; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state ──────────────────────────────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

if "linkedin_access_token" not in st.session_state:
    st.session_state.linkedin_access_token = None
    st.session_state.linkedin_profile_name = None
    st.session_state.linkedin_profile_title = None
    st.session_state.linkedin_profile_picture_url = None

# ── Init DB ────────────────────────────────────────────────────────────────────
db.ensure_tables()

# ── Header ─────────────────────────────────────────────────────────────────────
header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <span style="font-size:1.5rem;font-weight:800;color:#FAFAFA;">📊 FinSignal</span>
        </div>
        <div style="font-size:0.83rem;color:#6B7280;">
            LinkedIn Content Intelligence for Financial Crime Compliance
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    if st.session_state.linkedin_access_token:
        pic = st.session_state.linkedin_profile_picture_url or ""
        name = st.session_state.linkedin_profile_name or "Connected"
        title = st.session_state.linkedin_profile_title or "LinkedIn"
        if pic:
            st.markdown(
                f"""
                <div class="profile-chip">
                    <img class="profile-avatar" src="{pic}" />
                    <div>
                        <div class="profile-name">{name}</div>
                        <div class="profile-title">{title}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="profile-chip">
                    <div style="width:32px;height:32px;border-radius:50%;background:#0A66C2;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.85rem;">
                        {name[0].upper()}
                    </div>
                    <div>
                        <div class="profile-name">{name}</div>
                        <div class="profile-title">{title}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div style="text-align:right;padding-top:6px;">
                <a href="{API_URL}/auth/linkedin" target="_self"
                   style="background:#0A66C2;color:#fff;padding:8px 16px;border-radius:6px;
                          font-size:0.83rem;font-weight:600;text-decoration:none;">
                    🔗 Connect LinkedIn
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

# LinkedIn connect warning banner
if not st.session_state.linkedin_access_token:
    st.markdown(
        f"""
        <div class="li-banner">
            <span style="font-size:1.2rem;">⚠️</span>
            <span class="li-banner-text">
                <strong>Connect your LinkedIn account to enable posting.</strong>
                Approving posts and comments requires an active LinkedIn connection.
            </span>
            <a href="{API_URL}/auth/linkedin" target="_self"
               style="background:#F5A623;color:#0F1117;padding:6px 14px;border-radius:6px;
                      font-size:0.8rem;font-weight:700;text-decoration:none;white-space:nowrap;">
                Connect LinkedIn →
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Metrics row ────────────────────────────────────────────────────────────────
metrics = db.get_metrics()

c1, c2, c3, c4, c5 = st.columns(5)


def _next_agent_run() -> str:
    """Return countdown string to next scheduled agent run (ET approximation)."""
    now_utc = datetime.now(timezone.utc)
    now_et = now_utc - timedelta(hours=5)  # EST approximation
    candidates = []
    # Scraper: 6:00 AM ET
    for day_offset in [0, 1]:
        t = (now_et + timedelta(days=day_offset)).replace(hour=6, minute=0, second=0, microsecond=0)
        if t > now_et:
            candidates.append(t)
            break
    # Comments: 6:30 AM ET
    for day_offset in [0, 1]:
        t = (now_et + timedelta(days=day_offset)).replace(hour=6, minute=30, second=0, microsecond=0)
        if t > now_et:
            candidates.append(t)
            break
    # Research: every 4 hours at 2,6,10,14,18,22
    for h in [2, 6, 10, 14, 18, 22]:
        for day_offset in [0, 1]:
            t = (now_et + timedelta(days=day_offset)).replace(hour=h, minute=0, second=0, microsecond=0)
            if t > now_et:
                candidates.append(t)
                break
    if not candidates:
        return "—"
    nxt = min(candidates)
    delta = nxt - now_et
    total_mins = int(delta.total_seconds() / 60)
    h, m = divmod(total_mins, 60)
    return f"{h}h {m}m" if h else f"{m}m"


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
    if st.button("📝 View Content →", key="nav_content", use_container_width=True):
        st.session_state.active_tab = 0
        st.rerun()

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
    if st.button("📋 Review Drafts →", key="nav_drafts", use_container_width=True):
        st.session_state.active_tab = 0
        st.rerun()

with c3:
    pending = metrics['pending_comments']
    badge = f" ({pending})" if pending else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Comments Queued</div>
            <div class="metric-value">{pending}</div>
            <div class="metric-sub">pending approval</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"💬 Comment Inbox{badge} →", key="nav_comments", use_container_width=True):
        st.session_state.active_tab = 1
        st.rerun()

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
    if st.button("🤝 View Influencers →", key="nav_influencers", use_container_width=True):
        st.session_state.active_tab = 2
        st.rerun()

with c5:
    countdown = _next_agent_run()
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Next Agent Run</div>
            <div class="metric-value" style="font-size:1.5rem;">{countdown}</div>
            <div class="metric-sub">scraper · research · comments</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:31px'></div>", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Custom tab nav ─────────────────────────────────────────────────────────────
pending_count = metrics["pending_comments"]
tab_labels = [
    "📝  Content Queue",
    f"💬  Comment Queue{f'  ({pending_count})' if pending_count else ''}",
    "🤝  Influencer Manager",
]

t1, t2, t3 = st.columns(3)
tab_cols = [t1, t2, t3]

for i, (col, label) in enumerate(zip(tab_cols, tab_labels)):
    with col:
        is_active = st.session_state.active_tab == i
        if st.button(
            label,
            key=f"tab_nav_{i}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state.active_tab = i
            st.rerun()

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Tab content ────────────────────────────────────────────────────────────────
active = st.session_state.active_tab

if active == 0:
    content_queue.render(api_url=API_URL)
elif active == 1:
    comment_queue.render(api_url=API_URL)
elif active == 2:
    influencer_manager.render()
