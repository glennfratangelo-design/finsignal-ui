"""
Feed Manager page — manage RSS/blog feeds monitored by the research agent.
"""

import re
import streamlit as st
import db

_ALL_CATEGORIES = [
    "AML", "KYC", "Fraud", "Sanctions", "RegTech",
    "Regulatory", "Compliance", "Financial Crime", "Payments", "Other",
]

_CAT_COLORS = {
    "AML":            "#0A66C2",
    "KYC":            "#057642",
    "Fraud":          "#CC1016",
    "Sanctions":      "#E85D04",
    "RegTech":        "#7B2D8B",
    "Regulatory":     "#0891B2",
    "Compliance":     "#6366F1",
    "Financial Crime":"#DC2626",
    "Payments":       "#0284C7",
    "Other":          "#6B7280",
}

_CSS = """
<style>
.feed-card {
    background: #1E2130;
    border-radius: 8px;
    border: 1px solid #2D3748;
    padding: 14px 16px;
    margin-bottom: 0;
    position: relative;
}
.feed-card.priority { border-left: 4px solid #F5A623; }
.feed-card.standard { border-left: 4px solid #0A66C2; }
.feed-card.inactive { opacity: 0.45; }
.feed-card-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.feed-card-url {
    font-size: 0.72rem;
    color: #6B7280;
    word-break: break-all;
    margin-bottom: 8px;
}
.feed-card-url a { color: #0A66C2; text-decoration: none; }
.feed-card-meta { font-size: 0.72rem; color: #6B7280; margin-top: 6px; }
.cat-pill {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 20px;
    font-size: 0.67rem;
    font-weight: 700;
    color: #fff;
}
.home-badge {
    display: inline-block;
    background: #2A1A00;
    border: 1px solid #F5A623;
    color: #F5A623;
    font-size: 0.67rem;
    font-weight: 700;
    padding: 1px 7px;
    border-radius: 20px;
}
.inactive-badge {
    display: inline-block;
    background: #2D3748;
    color: #9AA0B2;
    font-size: 0.67rem;
    font-weight: 600;
    padding: 1px 7px;
    border-radius: 20px;
}
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 0.78rem;
    color: #6B7280;
    margin-bottom: 14px;
}
.add-form-panel {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 20px;
}
</style>
"""


def _cat_pill(category: str) -> str:
    color = _CAT_COLORS.get(category, "#555")
    return f'<span class="cat-pill" style="background:{color};">{category}</span>'


def _truncate_url(url: str, n: int = 55) -> str:
    return url[:n] + "…" if len(url) > n else url


def _is_valid_url(url: str) -> bool:
    return bool(re.match(r"https?://[^\s]+", url.strip()))


def _render_feed_card(row: dict, border_cls: str) -> None:
    row_id = row["id"]
    name = row["name"]
    url = row.get("url") or ""
    category = row.get("category") or "Other"
    active = int(row.get("active", 1))
    last_fetched = row.get("last_fetched")
    last_str = last_fetched[:16] if last_fetched else "Never"
    is_home = "niceactimize" in url.lower()
    inactive_cls = " inactive" if not active else ""

    home_badge = '<span class="home-badge">🏠 Home</span>' if is_home else ""
    inactive_badge = '<span class="inactive-badge">Paused</span>' if not active else ""

    st.markdown(
        f"""
        <div class="feed-card {border_cls}{inactive_cls}">
            <div class="feed-card-name">
                {name} {home_badge} {inactive_badge}
            </div>
            <div class="feed-card-url">
                <a href="{url}" target="_blank">{_truncate_url(url)}</a>
            </div>
            {_cat_pill(category)}
            <div class="feed-card-meta">Last fetched: {last_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_a, btn_b, btn_c, btn_spacer = st.columns([1, 1, 1, 3])

    with btn_a:
        toggle_label = "⏸ Pause" if active else "▶ Resume"
        if st.button(toggle_label, key=f"feed_toggle_{row_id}", use_container_width=True):
            db.toggle_feed_active(row_id, 0 if active else 1)
            st.rerun()

    with btn_b:
        if st.button("✏️ Edit", key=f"feed_edit_{row_id}", use_container_width=True):
            st.session_state["feed_editing"] = row_id
            st.session_state["feed_adding"] = False
            st.rerun()

    with btn_c:
        if st.button("🗑️ Delete", key=f"feed_delete_{row_id}", use_container_width=True):
            db.delete_feed(row_id)
            if st.session_state.get("feed_editing") == row_id:
                st.session_state["feed_editing"] = None
            st.rerun()

    # Inline edit form
    if st.session_state.get("feed_editing") == row_id:
        _render_feed_form(
            key_prefix=f"edit_{row_id}",
            defaults={
                "name": name,
                "url": url,
                "feed_type": row.get("feed_type", "rss"),
                "priority": row.get("priority", "standard"),
                "category": category,
                "active": bool(active),
            },
            on_save=lambda d: (
                db.update_feed(row_id, d["name"], d["url"], d["feed_type"], d["priority"], d["category"], int(d["active"])),
                st.session_state.update({"feed_editing": None}),
            ),
            on_cancel=lambda: st.session_state.update({"feed_editing": None}),
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def _render_feed_form(key_prefix: str, defaults: dict, on_save, on_cancel) -> None:
    st.markdown('<div class="add-form-panel">', unsafe_allow_html=True)
    with st.form(key=f"feed_form_{key_prefix}"):
        fc1, fc2 = st.columns(2)
        with fc1:
            new_name = st.text_input("Feed Name *", value=defaults.get("name", ""))
            new_url = st.text_input("Feed URL *", value=defaults.get("url", ""), placeholder="https://example.com/feed/")
            new_type = st.selectbox(
                "Feed Type",
                ["rss", "atom", "blog", "json"],
                index=["rss", "atom", "blog", "json"].index(defaults.get("feed_type", "rss")),
            )
        with fc2:
            new_category = st.selectbox(
                "Category",
                _ALL_CATEGORIES,
                index=_ALL_CATEGORIES.index(defaults.get("category", "Other")) if defaults.get("category") in _ALL_CATEGORIES else 0,
            )
            new_priority = st.radio(
                "Priority",
                ["standard", "priority"],
                index=0 if defaults.get("priority", "standard") == "standard" else 1,
                horizontal=True,
                format_func=lambda x: "⭐ Priority" if x == "priority" else "📡 Standard",
            )
            new_active = st.checkbox("Active (fetched by agent)", value=defaults.get("active", True))

        sc, cc = st.columns(2)
        with sc:
            if st.form_submit_button("💾 Save Feed", use_container_width=True):
                if not new_name.strip():
                    st.error("Feed name is required.")
                elif not _is_valid_url(new_url):
                    st.error("Enter a valid URL starting with http:// or https://")
                else:
                    on_save({
                        "name": new_name.strip(),
                        "url": new_url.strip(),
                        "feed_type": new_type,
                        "priority": new_priority,
                        "category": new_category,
                        "active": new_active,
                    })
                    st.rerun()
        with cc:
            if st.form_submit_button("Cancel", use_container_width=True):
                on_cancel()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Init session state ─────────────────────────────────────────────────────
    if "feed_editing" not in st.session_state:
        st.session_state.feed_editing = None
    if "feed_adding" not in st.session_state:
        st.session_state.feed_adding = False

    # ── Header row ─────────────────────────────────────────────────────────────
    hdr, hdr_btn = st.columns([5, 1])
    with hdr:
        st.markdown("### 📡 Feed Manager")
    with hdr_btn:
        if st.button(
            "➕ Add Feed" if not st.session_state.feed_adding else "✕ Cancel",
            key="feed_add_toggle",
            use_container_width=True,
            type="primary" if not st.session_state.feed_adding else "secondary",
        ):
            st.session_state.feed_adding = not st.session_state.feed_adding
            st.session_state.feed_editing = None
            st.rerun()

    # ── Add feed form ──────────────────────────────────────────────────────────
    if st.session_state.feed_adding:
        _render_feed_form(
            key_prefix="new",
            defaults={"feed_type": "rss", "priority": "standard", "category": "AML", "active": True},
            on_save=lambda d: (
                db.save_feed(d["name"], d["url"], d["feed_type"], d["priority"], d["category"], int(d["active"])),
                st.session_state.update({"feed_adding": False}),
            ),
            on_cancel=lambda: st.session_state.update({"feed_adding": False}),
        )

    all_feeds = db.get_feeds()
    priority_feeds = [f for f in all_feeds if f["priority"] == "priority"]
    standard_feeds = [f for f in all_feeds if f["priority"] != "priority"]
    active_count   = sum(1 for f in all_feeds if f["active"])

    st.markdown(
        f"<div style='font-size:0.78rem;color:#6B7280;margin-bottom:20px;'>"
        f"{len(all_feeds)} feeds total · {active_count} active</div>",
        unsafe_allow_html=True,
    )

    # ── Section 1: Priority Feeds ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="section-header">⭐ Priority Feeds</div>
        <div class="section-sub">Monitored first on every research cycle</div>
        """,
        unsafe_allow_html=True,
    )

    if not priority_feeds:
        st.markdown(
            '<div style="color:#6B7280;font-size:0.88rem;padding:16px 0 24px;">No priority feeds configured.</div>',
            unsafe_allow_html=True,
        )
    else:
        cols_p = st.columns(2)
        for i, feed in enumerate(priority_feeds):
            with cols_p[i % 2]:
                _render_feed_card(feed, "priority")

    st.markdown("<hr style='border-color:#2D3748;margin:20px 0;'>", unsafe_allow_html=True)

    # ── Section 2: Standard Feeds ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="section-header">📡 Standard Feeds</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if not standard_feeds:
        st.markdown(
            '<div style="color:#6B7280;font-size:0.88rem;padding:16px 0;">No standard feeds yet. Add one above.</div>',
            unsafe_allow_html=True,
        )
    else:
        cols_s = st.columns(3)
        for i, feed in enumerate(standard_feeds):
            with cols_s[i % 3]:
                _render_feed_card(feed, "standard")
