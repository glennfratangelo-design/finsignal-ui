"""
Analytics page — content pipeline health and post quality scorer.
"""

import streamlit as st
import db

_CSS = """
<style>
.analytics-card {
    background: #1E2130;
    border-radius: 8px;
    padding: 16px 18px;
    border: 1px solid #2D3748;
    min-height: 90px;
}
.analytics-label {
    font-size: 0.72rem;
    color: #9AA0B2;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}
.analytics-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FAFAFA;
    line-height: 1.1;
}
.analytics-sub {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 3px;
}
.score-bar-container {
    background: #2D3748;
    border-radius: 4px;
    height: 10px;
    margin-top: 4px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}
.locked-card {
    background: #161820;
    border-radius: 8px;
    border: 1px dashed #2D3748;
    padding: 24px;
    text-align: center;
    color: #4B5563;
}
.locked-icon { font-size: 1.8rem; margin-bottom: 8px; }
.locked-title { font-size: 0.88rem; font-weight: 700; color: #6B7280; margin-bottom: 4px; }
.locked-sub { font-size: 0.78rem; color: #4B5563; }
</style>
"""


def _score_color(score: int) -> str:
    if score >= 8:
        return "#22C55E"
    if score >= 6:
        return "#F5A623"
    return "#EF4444"


def _score_bar(label: str, score: int) -> str:
    pct   = score * 10
    color = _score_color(score)
    return f"""
    <div style='margin-bottom:10px;'>
        <div style='display:flex;justify-content:space-between;font-size:0.78rem;color:#9AA0B2;'>
            <span>{label}</span>
            <span style='color:{color};font-weight:700;'>{score}/10</span>
        </div>
        <div class='score-bar-container'>
            <div class='score-bar-fill' style='width:{pct}%;background:{color};'></div>
        </div>
    </div>
    """


def render(api_url: str = "") -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
        "📊 Analytics</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:20px;'>"
        "Content pipeline health, post quality scoring, and LinkedIn performance.</div>",
        unsafe_allow_html=True,
    )

    # LinkedIn status banner
    li_connected = st.session_state.get("linkedin_access_token") is not None
    if li_connected:
        name = st.session_state.get("linkedin_profile_name", "Connected")
        st.markdown(
            f"""<div style='background:#0D2137;border:1px solid #0A66C2;border-radius:8px;
                           padding:10px 16px;margin-bottom:16px;font-size:0.83rem;color:#60A5FA;'>
                ✅ LinkedIn connected as <strong>{name}</strong> — full analytics available.
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div style='background:#1A1C2A;border:1px solid #F5A623;border-radius:8px;
                           padding:10px 16px;margin-bottom:16px;display:flex;align-items:center;
                           gap:12px;'>
                <span style='font-size:1.1rem;'>⚠️</span>
                <span style='font-size:0.83rem;color:#F5A623;flex:1;'>
                    <strong>LinkedIn not connected.</strong>
                    Some analytics require an active LinkedIn connection.
                </span>
                <a href='{api_url}/auth/linkedin' target='_self'
                   style='background:#F5A623;color:#0F1117;padding:6px 14px;border-radius:6px;
                          font-size:0.8rem;font-weight:700;text-decoration:none;white-space:nowrap;'>
                    Connect →
                </a>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Content Pipeline Health ─────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:1rem;font-weight:700;color:#FAFAFA;margin-bottom:12px;'>"
        "Content Pipeline Health</div>",
        unsafe_allow_html=True,
    )

    metrics = db.get_metrics()
    health  = db.get_strategy_health()
    cfg     = db.get_strategy()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""<div class='analytics-card'>
                <div class='analytics-label'>Posts This Week</div>
                <div class='analytics-value'>{metrics['posts_this_week']}</div>
                <div class='analytics-sub'>of {health['max_posts_week']} max</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class='analytics-card'>
                <div class='analytics-label'>Drafts Pending</div>
                <div class='analytics-value'>{metrics['draft_count']}</div>
                <div class='analytics-sub'>awaiting review</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class='analytics-card'>
                <div class='analytics-label'>Archived (Quality)</div>
                <div class='analytics-value'>{health['archived_this_week']}</div>
                <div class='analytics-sub'>rejected this week</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        min_score = int(cfg.get("min_post_quality_score", 7))
        st.markdown(
            f"""<div class='analytics-card'>
                <div class='analytics-label'>Quality Threshold</div>
                <div class='analytics-value'>{min_score}/10</div>
                <div class='analytics-sub'>min score to publish</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Post Quality Scorer ──────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:1rem;font-weight:700;color:#FAFAFA;margin-bottom:8px;'>"
        "Post Quality Scorer</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:12px;'>"
        "Paste a LinkedIn post draft to get an AI quality score.</div>",
        unsafe_allow_html=True,
    )

    scorer_col, results_col = st.columns([3, 2])

    with scorer_col:
        post_text = st.text_area(
            "Paste post text here",
            height=220,
            placeholder="Paste your LinkedIn post draft...",
            key="analytics_post_text",
            label_visibility="collapsed",
        )
        score_btn = st.button("🎯 Score Post", key="analytics_score_btn", type="primary", use_container_width=True)

    with results_col:
        if score_btn:
            if not post_text.strip():
                st.warning("Paste a post first.")
            else:
                with st.spinner("Scoring with Claude..."):
                    scores = db.score_post(post_text.strip())

                overall = scores["overall"]
                color   = _score_color(overall)

                st.markdown(
                    f"""<div style='background:#1E2130;border:1px solid #2D3748;border-radius:8px;
                                   padding:16px 18px;'>
                        <div style='font-size:0.72rem;color:#9AA0B2;text-transform:uppercase;
                                    letter-spacing:.07em;margin-bottom:4px;'>Overall Score</div>
                        <div style='font-size:2.5rem;font-weight:800;color:{color};
                                    line-height:1;margin-bottom:12px;'>{overall}/10</div>
                        {_score_bar("Hook", scores["hook"])}
                        {_score_bar("Data / Insight", scores["data"])}
                        {_score_bar("Readability", scores["readability"])}
                        {_score_bar("Call to Action", scores["cta"])}
                    </div>""",
                    unsafe_allow_html=True,
                )
                if scores["suggestion"]:
                    st.markdown(
                        f"""<div style='background:#2D2010;border:1px solid #F5A623;border-radius:6px;
                                       padding:10px 14px;margin-top:10px;font-size:0.83rem;color:#F5A623;'>
                            💡 {scores['suggestion']}
                        </div>""",
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                "<div style='background:#161820;border:1px dashed #2D3748;border-radius:8px;"
                "padding:40px 20px;text-align:center;color:#4B5563;height:280px;"
                "display:flex;align-items:center;justify-content:center;'>"
                "<div><div style='font-size:2rem;margin-bottom:8px;'>🎯</div>"
                "<div style='font-size:0.88rem;'>Score results will appear here</div></div>"
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Locked cards (LinkedIn-dependent) ─────────────────────────────────────
    st.markdown(
        "<div style='font-size:1rem;font-weight:700;color:#FAFAFA;margin-bottom:12px;'>"
        "LinkedIn Performance <span style='font-size:0.75rem;color:#6B7280;font-weight:400;'>"
        "— requires LinkedIn connection</span></div>",
        unsafe_allow_html=True,
    )

    lc1, lc2, lc3 = st.columns(3)
    for col, icon, title, sub in [
        (lc1, "📈", "Post Impressions", "Views, reach, and engagement rate per post"),
        (lc2, "💬", "Comment Performance", "Replies, likes, and follow-up engagement"),
        (lc3, "👥", "Follower Growth", "New followers gained from content activity"),
    ]:
        lock_color = "#22C55E" if li_connected else "#4B5563"
        with col:
            st.markdown(
                f"""<div class='locked-card'>
                    <div class='locked-icon'>{icon}</div>
                    <div class='locked-title' style='color:{lock_color};'>{title}</div>
                    <div class='locked-sub'>{sub}</div>
                    {"" if li_connected else
                     f"<div style='margin-top:12px;'><a href='{api_url}/auth/linkedin' target='_self' "
                     f"style='font-size:0.78rem;color:#0A66C2;text-decoration:none;'>🔗 Connect LinkedIn</a></div>"}
                </div>""",
                unsafe_allow_html=True,
            )
