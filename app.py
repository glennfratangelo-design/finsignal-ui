"""
FinSignal UI — Main entry point.
Streamlit dashboard for LinkedIn content management.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import streamlit as st
import db
from pages import content_queue, comment_queue, influencer_manager, strategy_manager, analytics, connections

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Pre-flight: abort if Streamlit runtime context not ready ───────────────────
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    if ctx is None:
        sys.exit(0)
except Exception:
    sys.exit(0)

# ── st.set_page_config MUST be the absolute first Streamlit command ────────────
st.set_page_config(
    page_title="FinSignal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:  # ── Wrap entire app body to catch SessionInfo errors ──────────────────────

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
        section[data-testid="stSidebar"] { display: none !important; }
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


    # ── LinkedIn session helpers ────────────────────────────────────────────────────

    def safe_get_query_params() -> dict:
        try:
            return dict(st.query_params)
        except Exception:
            return {}


    def init_linkedin_session() -> None:
        try:
            params = safe_get_query_params()
            if params.get("linkedin_connected") == "true":
                st.session_state.linkedin_profile = {
                    "name": params.get("name", ""),
                    "email": params.get("email", ""),
                    "picture_url": params.get("picture", ""),
                }
                st.session_state.linkedin_connected = True
                try:
                    st.query_params.clear()
                except Exception:
                    pass
            elif not st.session_state.get("linkedin_connected"):
                # Try to restore from persisted token in backend DB
                _profile = db.get_linkedin_profile()
                if _profile.get("connected"):
                    st.session_state.linkedin_profile = {
                        "name": _profile.get("name", ""),
                        "email": _profile.get("headline") or _profile.get("email", ""),
                        "picture_url": _profile.get("picture_url", ""),
                    }
                    st.session_state.linkedin_connected = True
        except Exception as e:
            if "SessionInfo" in str(e) or "session" in str(e).lower():
                st.rerun()
            return


    # ── Session state initialization ───────────────────────────────────────────────

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    if "posts_range" not in st.session_state:
        st.session_state.posts_range = "7 Days"

    if "comments_range" not in st.session_state:
        st.session_state.comments_range = "7 Days"

    if "linkedin_connected" not in st.session_state:
        st.session_state.linkedin_connected = False

    if "linkedin_profile" not in st.session_state:
        st.session_state.linkedin_profile = {}

    if not st.session_state.get("linkedin_profile_checked"):
        db.ensure_tables()
        init_linkedin_session()
        st.session_state.linkedin_profile_checked = True


    # ── Header ─────────────────────────────────────────────────────────────────────
    header_left, header_right = st.columns([3, 1])

    with header_left:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                <span style="font-size:1.5rem;font-weight:800;color:#FAFAFA;">📊 FinSignal</span>
            </div>
            <div style="font-size:0.83rem;color:#6B7280;">
                Empowering your voice with autonomous intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_right:
        if st.session_state.get("linkedin_connected"):
            _lp   = st.session_state.get("linkedin_profile", {})
            pic   = _lp.get("picture_url", "") or ""
            name  = _lp.get("name", "") or "Connected"
            title = _lp.get("email", "") or "LinkedIn"
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
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("🔌 Disconnect LinkedIn", key="btn_logout", use_container_width=True):
                db.linkedin_logout()
                for _key in [
                    "linkedin_access_token",
                    "linkedin_profile_name",
                    "linkedin_profile_title",
                    "linkedin_profile_picture_url",
                    "linkedin_profile_checked",
                    "linkedin_profile",
                    "linkedin_connected",
                    "linkedin_profile_picture",
                    "linkedin_profile_email",
                    "session_initialized",
                ]:
                    st.session_state.pop(_key, None)
                st.rerun()
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
    if not st.session_state.get("linkedin_connected"):
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

    _range_param = {"Today": "today", "7 Days": "7days", "30 Days": "30days"}
    _range_labels = ["Today", "7 Days", "30 Days"]

    posts_metrics    = db.get_metrics(time_range=_range_param[st.session_state.posts_range])
    comments_metrics = db.get_metrics(time_range=_range_param[st.session_state.comments_range])

    posts_count      = posts_metrics["posts_count"]
    comments_count   = comments_metrics["comments_count"]
    pending_comments = posts_metrics["pending_comments"]  # not range-filtered

    c1, c2, c3 = st.columns(3)

    # ── Card 1: Posts ──────────────────────────────────────────────────────────
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Posts</div>
                <div class="metric-value">{posts_count}</div>
                <div class="metric-sub">posted to LinkedIn</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Posts →", key="nav_to_posts", use_container_width=True):
            st.session_state.active_tab = 0
            st.rerun()
        pr = st.session_state.posts_range
        p1, p2, p3 = st.columns(3)
        for _col, _lbl in zip([p1, p2, p3], _range_labels):
            with _col:
                if st.button(
                    _lbl,
                    key=f"pr_{_lbl}",
                    type="primary" if pr == _lbl else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.posts_range = _lbl
                    st.session_state.active_tab = 0
                    st.rerun()

    # ── Card 2: Comments ───────────────────────────────────────────────────────
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Comments</div>
                <div class="metric-value">{comments_count}</div>
                <div class="metric-sub">posted to LinkedIn</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Comments →", key="nav_to_comments", use_container_width=True):
            st.session_state.active_tab = 1
            st.rerun()
        cr = st.session_state.comments_range
        q1, q2, q3 = st.columns(3)
        for _col, _lbl in zip([q1, q2, q3], _range_labels):
            with _col:
                if st.button(
                    _lbl,
                    key=f"cr_{_lbl}",
                    type="primary" if cr == _lbl else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.comments_range = _lbl
                    st.session_state.active_tab = 1
                    st.rerun()

    # ── Card 3: Next Agent Run ─────────────────────────────────────────────────
    with c3:
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

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Quick Compose ──────────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:1.1rem;font-weight:700;color:#FAFAFA;margin-bottom:8px;'>"
        "✍️ Quick Compose</div>"
        "<div style='font-size:0.82rem;color:#6B7280;margin-bottom:10px;'>"
        "Write a prompt and AI will generate a LinkedIn post using your voice and ICP.</div>",
        unsafe_allow_html=True,
    )

    compose_prompt = st.text_area(
        "What do you want to post about?",
        placeholder="e.g. Write about the Treasury's new AI risk framework and what it means for CCOs managing AI-driven transaction monitoring...",
        key="compose_prompt",
        height=100,
        label_visibility="collapsed",
    )

    compose_col, _ = st.columns([1, 3])
    with compose_col:
        if st.button("🚀 Generate Post", key="compose_generate", type="primary", use_container_width=True):
            if compose_prompt and compose_prompt.strip():
                with st.spinner("Generating post with your voice..."):
                    try:
                        import requests as _req
                        r = _req.post(
                            f"{API_URL}/compose",
                            json={"prompt": compose_prompt.strip()},
                            timeout=30,
                        )
                        data = r.json()
                        if data.get("ok"):
                            st.toast(f"✅ Post created: {data.get('title', 'New post')}")
                            st.session_state.active_tab = 0
                            st.rerun()
                        else:
                            st.error(f"Failed: {data.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter a prompt first")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Custom tab nav ─────────────────────────────────────────────────────────────
    pending_count = pending_comments
    tab_labels = [
        "📝  Content Queue",
        f"💬  Comment Queue{f'  ({pending_count})' if pending_count else ''}",
        "🤝  Influencers",
        "⚙️  Strategy",
        "📊  Analytics",
        "🔗  Connections",
    ]

    t1, t2, t3, t4, t5, t6 = st.columns(6)
    tab_cols = [t1, t2, t3, t4, t5, t6]

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
    elif active == 3:
        strategy_manager.render()
    elif active == 4:
        analytics.render(api_url=API_URL)
    elif active == 5:
        connections.render()

except Exception as _app_err:
    _err_str = str(_app_err)
    if "SessionInfo" in _err_str or "session" in _err_str.lower():
        st.rerun()
    else:
        st.error(f"Application error: {_app_err}")
