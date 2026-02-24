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
    "AML":             "#0A66C2",
    "KYC":             "#057642",
    "Fraud":           "#CC1016",
    "Sanctions":       "#E85D04",
    "RegTech":         "#7B2D8B",
    "Regulatory":      "#0891B2",
    "Compliance":      "#6366F1",
    "Financial Crime": "#DC2626",
    "Payments":        "#0284C7",
    "Other":           "#6B7280",
}

_CSS = """
<style>
.feed-card {
    background: #1E2130;
    border-radius: 8px;
    border: 1px solid #2D3748;
    padding: 14px 16px;
    margin-bottom: 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.35);
}
.feed-card.priority { border-left: 3px solid #F5A623; }
.feed-card.standard { border-left: 3px solid #2D3748; }
.feed-card.inactive { opacity: 0.45; }
.feed-card-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 3px;
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
.add-form-panel {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 20px;
}
.list-header {
    font-size: 0.72rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 700;
    padding: 4px 0;
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


def _render_feed_form(key_prefix: str, defaults: dict, on_save, on_cancel) -> None:
    st.markdown('<div class="add-form-panel">', unsafe_allow_html=True)
    with st.form(key=f"feed_form_{key_prefix}"):
        fc1, fc2 = st.columns(2)
        with fc1:
            new_name = st.text_input("Feed Name *", value=defaults.get("name", ""))
            new_url  = st.text_input("Feed URL *", value=defaults.get("url", ""), placeholder="https://example.com/feed/")
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
                format_func=lambda x: "⭐ Priority" if x == "priority" else "Standard",
            )
            new_active = st.checkbox("Active (fetched by agent)", value=defaults.get("active", True))

        sc, cc = st.columns(2)
        with sc:
            if st.form_submit_button("Save Feed", use_container_width=True):
                if not new_name.strip():
                    st.error("Feed name is required.")
                elif not _is_valid_url(new_url):
                    st.error("Enter a valid URL starting with http:// or https://")
                else:
                    on_save({
                        "name":      new_name.strip(),
                        "url":       new_url.strip(),
                        "feed_type": new_type,
                        "priority":  new_priority,
                        "category":  new_category,
                        "active":    new_active,
                    })
                    st.rerun()
        with cc:
            if st.form_submit_button("Cancel", use_container_width=True):
                on_cancel()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_card_view(feed: dict) -> None:
    row_id    = feed["id"]
    name      = feed["name"]
    url       = feed.get("url") or ""
    category  = feed.get("category") or "Other"
    priority  = feed.get("priority") or "standard"
    feed_type = feed.get("feed_type") or "rss"
    active    = int(feed.get("active", 1))
    last_str  = (feed.get("last_fetched") or "")[:16] or "Never"
    is_home   = "niceactimize" in url.lower()

    border_cls   = "priority" if priority == "priority" else "standard"
    inactive_cls = " inactive" if not active else ""
    home_badge     = '<span class="home-badge">Home</span>' if is_home else ""
    inactive_badge = '<span class="inactive-badge">Paused</span>' if not active else ""

    st.markdown(
        f"""
        <div class="feed-card {border_cls}{inactive_cls}">
            <div class="feed-card-name">{name} {home_badge} {inactive_badge}</div>
            <div class="feed-card-url">
                <a href="{url}" target="_blank">{_truncate_url(url)}</a>
            </div>
            {_cat_pill(category)}
            <div class="feed-card-meta">Last fetched: {last_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    star_col, toggle_col, edit_col, del_col = st.columns(4)

    with star_col:
        star = "⭐" if priority == "priority" else "☆"
        if st.button(star, key=f"feed_star_{row_id}", help="Toggle priority", use_container_width=True):
            new_p = "standard" if priority == "priority" else "priority"
            db.update_feed(row_id, name, url, feed_type, new_p, category, active)
            st.rerun()

    with toggle_col:
        if st.button("⏸" if active else "▶", key=f"feed_toggle_{row_id}", help="Pause/Resume", use_container_width=True):
            db.toggle_feed_active(row_id, 0 if active else 1)
            st.rerun()

    with edit_col:
        if st.button("✏️", key=f"feed_edit_{row_id}", help="Edit", use_container_width=True):
            current = st.session_state.get("feed_editing")
            st.session_state["feed_editing"] = None if current == row_id else row_id
            st.session_state["feed_adding"]  = False
            st.rerun()

    with del_col:
        if st.button("🗑️", key=f"feed_del_{row_id}", help="Delete", use_container_width=True):
            db.delete_feed(row_id)
            if st.session_state.get("feed_editing") == row_id:
                st.session_state["feed_editing"] = None
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def _render_list_row(feed: dict) -> None:
    row_id    = feed["id"]
    name      = feed["name"]
    url       = feed.get("url") or ""
    category  = feed.get("category") or "Other"
    priority  = feed.get("priority") or "standard"
    feed_type = feed.get("feed_type") or "rss"
    active    = int(feed.get("active", 1))
    last_str  = (feed.get("last_fetched") or "")[:10] or "Never"

    c_info, c_cat, c_last, c_star, c_tog, c_edit, c_del = st.columns([3.5, 1.2, 1.2, 0.6, 0.6, 0.6, 0.6])

    with c_info:
        st.markdown(
            f"<div style='padding:6px 0;'>"
            f"<span style='font-size:0.88rem;font-weight:700;color:#FAFAFA;'>{name}</span>&nbsp;"
            f"<a href='{url}' target='_blank' style='font-size:0.72rem;color:#0A66C2;'>{_truncate_url(url, 40)}</a>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c_cat:
        st.markdown(f"<div style='padding:8px 0;'>{_cat_pill(category)}</div>", unsafe_allow_html=True)
    with c_last:
        st.markdown(
            f"<div style='padding:6px 0;font-size:0.72rem;color:#6B7280;'>{last_str}</div>",
            unsafe_allow_html=True,
        )
    with c_star:
        star = "⭐" if priority == "priority" else "☆"
        if st.button(star, key=f"feed_star_{row_id}", help="Toggle priority", use_container_width=True):
            new_p = "standard" if priority == "priority" else "priority"
            db.update_feed(row_id, name, url, feed_type, new_p, category, active)
            st.rerun()
    with c_tog:
        if st.button("⏸" if active else "▶", key=f"feed_toggle_{row_id}", help="Pause/Resume", use_container_width=True):
            db.toggle_feed_active(row_id, 0 if active else 1)
            st.rerun()
    with c_edit:
        if st.button("✏️", key=f"feed_edit_{row_id}", help="Edit", use_container_width=True):
            current = st.session_state.get("feed_editing")
            st.session_state["feed_editing"] = None if current == row_id else row_id
            st.session_state["feed_adding"]  = False
            st.rerun()
    with c_del:
        if st.button("🗑️", key=f"feed_del_{row_id}", help="Delete", use_container_width=True):
            db.delete_feed(row_id)
            if st.session_state.get("feed_editing") == row_id:
                st.session_state["feed_editing"] = None
            st.rerun()

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)


def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Init session state ─────────────────────────────────────────────────────
    for key, default in [("feed_editing", None), ("feed_adding", False), ("feed_view", "card")]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Header row ─────────────────────────────────────────────────────────────
    hdr, hdr_view, hdr_btn = st.columns([4, 1, 1])

    with hdr:
        st.markdown(
            "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
            "Feed Manager</div>"
            "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:16px;'>"
            "RSS and blog sources monitored by the research agent.</div>",
            unsafe_allow_html=True,
        )
    with hdr_view:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        view_icon = "☰ List" if st.session_state.feed_view == "card" else "⊞ Cards"
        if st.button(view_icon, key="feed_view_toggle", use_container_width=True):
            st.session_state.feed_view = "list" if st.session_state.feed_view == "card" else "card"
            st.rerun()
    with hdr_btn:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        add_label = "✕ Cancel" if st.session_state.feed_adding else "➕ Add Feed"
        btn_type  = "secondary" if st.session_state.feed_adding else "primary"
        if st.button(add_label, key="feed_add_toggle", use_container_width=True, type=btn_type):
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

    # ── Load feeds — priority first ────────────────────────────────────────────
    all_feeds      = db.get_feeds()
    priority_feeds = [f for f in all_feeds if f.get("priority") == "priority"]
    standard_feeds = [f for f in all_feeds if f.get("priority") != "priority"]
    sorted_feeds   = priority_feeds + standard_feeds
    active_count   = sum(1 for f in all_feeds if f.get("active"))

    st.markdown(
        f"<div style='font-size:0.78rem;color:#6B7280;margin-bottom:16px;'>"
        f"{len(all_feeds)} feeds &nbsp;·&nbsp; {len(priority_feeds)} priority &nbsp;·&nbsp; {active_count} active</div>",
        unsafe_allow_html=True,
    )

    if not sorted_feeds:
        st.markdown(
            "<div style='color:#6B7280;font-size:0.88rem;padding:40px 0;text-align:center;'>"
            "No feeds configured. Add one above.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Render ─────────────────────────────────────────────────────────────────
    if st.session_state.feed_view == "card":
        cols = st.columns(2)
        for i, feed in enumerate(sorted_feeds):
            with cols[i % 2]:
                _render_card_view(feed)
    else:
        # List view column headers
        lh1, lh2, lh3, _, _, _, _ = st.columns([3.5, 1.2, 1.2, 0.6, 0.6, 0.6, 0.6])
        for col, label in [(lh1, "Feed"), (lh2, "Category"), (lh3, "Last Fetched")]:
            col.markdown(
                f"<div class='list-header'>{label}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        for feed in sorted_feeds:
            _render_list_row(feed)

    # ── Inline edit form (full width, below grid) ──────────────────────────────
    editing_id = st.session_state.get("feed_editing")
    if editing_id:
        editing_feed = next((f for f in sorted_feeds if f["id"] == editing_id), None)
        if editing_feed:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _render_feed_form(
                key_prefix=f"edit_{editing_id}",
                defaults={
                    "name":      editing_feed["name"],
                    "url":       editing_feed.get("url", ""),
                    "feed_type": editing_feed.get("feed_type", "rss"),
                    "priority":  editing_feed.get("priority", "standard"),
                    "category":  editing_feed.get("category", "Other"),
                    "active":    bool(int(editing_feed.get("active", 1))),
                },
                on_save=lambda d: (
                    db.update_feed(editing_id, d["name"], d["url"], d["feed_type"], d["priority"], d["category"], int(d["active"])),
                    st.session_state.update({"feed_editing": None}),
                ),
                on_cancel=lambda: st.session_state.update({"feed_editing": None}),
            )
