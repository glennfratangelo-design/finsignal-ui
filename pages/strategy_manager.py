"""
Strategy Manager page — configure posting strategy, comment rules, and quality gates.
"""

import streamlit as st
import db

_CSS = """
<style>
.health-card {
    background: #1E2130;
    border-radius: 8px;
    padding: 16px 18px;
    border: 1px solid #2D3748;
    min-height: 90px;
}
.health-card.warn { border-left: 3px solid #F5A623; }
.health-card.ok   { border-left: 3px solid #22C55E; }
.health-label {
    font-size: 0.72rem;
    color: #9AA0B2;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}
.health-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FAFAFA;
    line-height: 1.1;
}
.health-sub {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 3px;
}
.flagged-item {
    background: #2D2010;
    border: 1px solid #F5A623;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 0.83rem;
    color: #F5A623;
    margin-bottom: 6px;
}
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 12px;
}
</style>
"""


def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
        "⚙️ Strategy Manager</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:20px;'>"
        "Configure posting limits, content mix, comment rules, and quality gates.</div>",
        unsafe_allow_html=True,
    )

    cfg = db.get_strategy()
    health = db.get_strategy_health()

    # ── Section 1: Strategy Health ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>Strategy Health</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    comments_today  = health["comments_today"]
    max_comments    = health["max_comments_day"]
    posts_week      = health["posts_this_week"]
    max_posts       = health["max_posts_week"]
    archived        = health["archived_this_week"]

    with c1:
        warn = comments_today >= max_comments
        cls  = "warn" if warn else "ok"
        st.markdown(
            f"""<div class='health-card {cls}'>
                <div class='health-label'>Comments Today</div>
                <div class='health-value'>{comments_today}/{max_comments}</div>
                <div class='health-sub'>{'⚠️ Limit reached' if warn else 'Within limit'}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        warn = posts_week >= max_posts
        cls  = "warn" if warn else "ok"
        st.markdown(
            f"""<div class='health-card {cls}'>
                <div class='health-label'>Posts This Week</div>
                <div class='health-value'>{posts_week}/{max_posts}</div>
                <div class='health-sub'>{'⚠️ Limit reached' if warn else 'Within limit'}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        pct = round((posts_week / max_posts) * 100) if max_posts else 0
        st.markdown(
            f"""<div class='health-card ok'>
                <div class='health-label'>Weekly Pacing</div>
                <div class='health-value'>{pct}%</div>
                <div class='health-sub'>of weekly target used</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        warn = archived > 0
        cls  = "warn" if warn else "ok"
        st.markdown(
            f"""<div class='health-card {cls}'>
                <div class='health-label'>Archived (Quality)</div>
                <div class='health-value'>{archived}</div>
                <div class='health-sub'>posts failed quality gate this week</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Topic distribution bar chart
    topic_dist    = health.get("topic_distribution", {})
    target_weights = health.get("target_weights", {})
    if topic_dist:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header' style='font-size:0.88rem;'>Topic Distribution This Week</div>", unsafe_allow_html=True)
        bar_cols = st.columns(len(topic_dist))
        for col, (topic, count) in zip(bar_cols, topic_dist.items()):
            target = target_weights.get(topic, 0)
            target_posts = round((target / 100) * max_posts) if target else 0
            label = f"{topic}\n{count}/{target_posts}"
            col.metric(label=topic, value=count, delta=f"target {target_posts}")

    # Flagged items
    flagged = health.get("flagged_items", [])
    if flagged:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        for item in flagged:
            st.markdown(f"<div class='flagged-item'>{item}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Section 2: Posting Strategy ────────────────────────────────────────────
    with st.expander("📝 Posting Strategy", expanded=False):
        col_l, col_r = st.columns(2)

        with col_l:
            new_max_posts_day = st.number_input(
                "Max posts per day",
                min_value=1, max_value=10,
                value=int(cfg.get("max_posts_per_day", 2)),
                key="strat_max_posts_day",
            )
            new_max_posts_week = st.number_input(
                "Max posts per week",
                min_value=1, max_value=30,
                value=int(cfg.get("max_posts_per_week", 8)),
                key="strat_max_posts_week",
            )

        with col_r:
            times_raw = cfg.get("best_posting_times", ["08:00", "12:00", "17:00"])
            times_str = st.text_input(
                "Best posting times (comma-separated, 24h)",
                value=", ".join(times_raw),
                key="strat_post_times",
            )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("**Topic Allocation (must total 100%)**")

        weights = dict(cfg.get("topic_weights", {"AML": 30, "KYC": 15, "Fraud": 20, "AI/Agentic": 25, "Sanctions": 10}))
        new_weights = {}
        wc = st.columns(len(weights))
        for i, (topic, pct) in enumerate(weights.items()):
            with wc[i]:
                new_weights[topic] = st.slider(topic, 0, 100, int(pct), key=f"strat_weight_{topic}")

        total_pct = sum(new_weights.values())
        pct_color = "#22C55E" if total_pct == 100 else "#F5A623"
        st.markdown(
            f"<span style='font-size:0.83rem;color:{pct_color};'>Total: {total_pct}%</span>",
            unsafe_allow_html=True,
        )
        if total_pct != 100 and st.button("⚖️ Rebalance to 100%", key="strat_rebalance"):
            if total_pct > 0:
                scale = 100 / total_pct
                new_weights = {k: max(1, round(v * scale)) for k, v in new_weights.items()}
                # Adjust rounding error on largest
                diff = 100 - sum(new_weights.values())
                if diff != 0:
                    biggest = max(new_weights, key=new_weights.get)
                    new_weights[biggest] += diff
                st.rerun()

        if st.button("💾 Save Posting Strategy", key="strat_save_posting", type="primary"):
            times_list = [t.strip() for t in times_str.split(",") if t.strip()]
            db.update_strategy({
                "max_posts_per_day":  new_max_posts_day,
                "max_posts_per_week": new_max_posts_week,
                "best_posting_times": times_list,
                "topic_weights":      new_weights,
            })
            st.toast("✓ Posting strategy saved", icon="✅")

    # ── Section 3: Comment Co-Pilot ────────────────────────────────────────────
    with st.expander("💬 Comment Co-Pilot", expanded=False):
        col_l, col_r = st.columns(2)

        with col_l:
            new_max_comments_day = st.number_input(
                "Max comments per day",
                min_value=1, max_value=20,
                value=int(cfg.get("max_comments_per_day", 5)),
                key="strat_max_comments_day",
            )
            new_max_per_inf = st.number_input(
                "Max comments per influencer per week",
                min_value=1, max_value=10,
                value=int(cfg.get("max_comments_per_influencer_per_week", 2)),
                key="strat_max_per_inf",
            )
            new_cooldown = st.number_input(
                "Cooldown hours between comments",
                min_value=1, max_value=168,
                value=int(cfg.get("comment_cooldown_hours", 48)),
                key="strat_cooldown",
            )

        with col_r:
            tone_rules = cfg.get("comment_tone_rules", [])
            tone_raw   = st.text_area(
                "Tone rules (one per line)",
                value="\n".join(tone_rules),
                height=130,
                key="strat_tone_rules",
            )
            avoided_raw = st.text_area(
                "Avoided intent keywords (one per line)",
                value="\n".join(cfg.get("avoided_intent_keywords", [])),
                height=100,
                key="strat_avoided",
            )

        never_raw = st.text_input(
            "Never-comment accounts (comma-separated handles)",
            value=", ".join(cfg.get("never_comment_accounts", [])),
            key="strat_never_accounts",
        )

        if st.button("💾 Save Comment Co-Pilot", key="strat_save_comments", type="primary"):
            db.update_strategy({
                "max_comments_per_day":                  new_max_comments_day,
                "max_comments_per_influencer_per_week":  new_max_per_inf,
                "comment_cooldown_hours":                new_cooldown,
                "comment_tone_rules":                    [r.strip() for r in tone_raw.splitlines() if r.strip()],
                "avoided_intent_keywords":               [k.strip() for k in avoided_raw.splitlines() if k.strip()],
                "never_comment_accounts":                [a.strip() for a in never_raw.split(",") if a.strip()],
            })
            st.toast("✓ Comment settings saved", icon="✅")

    # ── Section 4: Quality Gate ─────────────────────────────────────────────────
    with st.expander("🎯 Quality Gate", expanded=False):
        st.markdown(
            "<div style='font-size:0.83rem;color:#9AA0B2;margin-bottom:12px;'>"
            "Posts scoring below the minimum threshold will be regenerated once. "
            "If still below, they're archived and excluded from the content queue.</div>",
            unsafe_allow_html=True,
        )
        col_l, col_r = st.columns([2, 1])
        with col_l:
            new_min_score = st.slider(
                "Minimum post quality score (1–10)",
                min_value=1, max_value=10,
                value=int(cfg.get("min_post_quality_score", 7)),
                key="strat_min_score",
            )
        with col_r:
            st.markdown(
                f"""<div class='health-card ok' style='margin-top:6px;'>
                    <div class='health-label'>Archived This Week</div>
                    <div class='health-value'>{archived}</div>
                    <div class='health-sub'>posts rejected</div>
                </div>""",
                unsafe_allow_html=True,
            )

        if st.button("💾 Save Quality Gate", key="strat_save_quality", type="primary"):
            db.update_strategy({"min_post_quality_score": new_min_score})
            st.toast("✓ Quality gate saved", icon="✅")
