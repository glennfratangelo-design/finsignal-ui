"""
Influencer Manager — Watchlist + Discover tabs.
"""

import streamlit as st
import db

_ALL_NICHES = ["AML", "KYC", "Fraud", "Sanctions", "RegTech", "AI/Agentic", "Compliance", "Regulatory"]

_NICHE_COLORS = {
    "AML":        "#0A66C2",
    "Fraud":      "#CC1016",
    "KYC":        "#057642",
    "Sanctions":  "#E85D04",
    "RegTech":    "#7B2D8B",
    "AI/Agentic": "#0891B2",
    "Compliance": "#6366F1",
    "Regulatory": "#DC2626",
}

_CSS = """
<style>
.inf-row {
    display: flex;
    align-items: center;
    padding: 10px 14px;
    border-bottom: 1px solid #2D3748;
    gap: 12px;
}
.inf-row:hover { background: #1A1C2A; }
.inf-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #FAFAFA;
    flex: 2;
}
.inf-handle {
    font-size: 0.82rem;
    color: #0A66C2;
    flex: 2;
}
.inf-handle a { color: #0A66C2; text-decoration: none; }
.inf-handle a:hover { text-decoration: underline; }
.pill {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #fff;
    margin-right: 4px;
}
.pill-active    { background: #057642; }
.pill-hibernated { background: #92400E; color: #FDE68A; }
.discover-card {
    background: #1E2130;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.discover-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 2px;
}
.discover-headline {
    font-size: 0.8rem;
    color: #9AA0B2;
    margin-bottom: 8px;
}
.discover-reason {
    font-size: 0.83rem;
    color: #CBD5E1;
    font-style: italic;
    margin-bottom: 10px;
    line-height: 1.5;
}
.pattern-card {
    background: #1A2744;
    border: 1px solid #2563EB;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 0.85rem;
    color: #93C5FD;
    line-height: 1.5;
}
.add-form-panel {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 16px;
}
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.88rem;
    padding: 48px 0;
}
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 10px;
}
</style>
"""


def _niche_pill(niche: str) -> str:
    color = _NICHE_COLORS.get(niche, "#374151")
    return f'<span class="pill" style="background:{color};">{niche or "—"}</span>'


def _status_pill(status: str) -> str:
    if status == "hibernated":
        return '<span class="pill pill-hibernated">Hibernated</span>'
    return '<span class="pill pill-active">Active</span>'


def _init_im_states() -> None:
    defaults = {
        "im_tab":            0,     # 0=Watchlist, 1=Discover
        "im_filter":         "All", # All / Active / Hibernated
        "im_show_add":       False,
        "im_remove_confirm": None,  # id of row pending confirmation
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Watchlist tab ─────────────────────────────────────────────────────────────

def _render_watchlist() -> None:
    # Header row
    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        count_row = db.get_influencers()
        total = len(count_row)
        st.markdown(
            f"<div class='section-header'>Watchlist "
            f"<span style='font-size:0.78rem;font-weight:400;color:#9AA0B2;'>"
            f"({total})</span></div>",
            unsafe_allow_html=True,
        )
    with hdr_r:
        showing = st.session_state.im_show_add
        if st.button(
            "✕ Cancel" if showing else "➕ Add Influencer",
            key="im_toggle_add",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.im_show_add = not showing
            st.rerun()

    # Add form
    if st.session_state.im_show_add:
        st.markdown("<div class='add-form-panel'>", unsafe_allow_html=True)
        with st.form("im_add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_name   = st.text_input("Full Name *", placeholder="e.g. Kieran Beer")
                new_handle = st.text_input("LinkedIn Handle *", placeholder="kieranbeer  (no @)")
            with c2:
                new_niche = st.selectbox("Niche", _ALL_NICHES)
                new_notes = st.text_input("Notes (optional)", placeholder="Optional context")
            save_col, _ = st.columns([1, 3])
            with save_col:
                submitted = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
            if submitted:
                if not new_name.strip() or not new_handle.strip():
                    st.error("Name and handle are required.")
                else:
                    db.add_influencer(
                        name=new_name.strip(),
                        linkedin_handle=new_handle.strip().lstrip("@"),
                        niche=new_niche,
                        notes=new_notes.strip(),
                    )
                    st.session_state.im_show_add = False
                    st.toast(f"Added {new_name.strip()} to watchlist")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Filter chips
    filter_cols = st.columns([1, 1, 1, 6])
    for i, label in enumerate(["All", "Active", "Hibernated"]):
        with filter_cols[i]:
            is_active = st.session_state.im_filter == label
            if st.button(
                label,
                key=f"im_filter_{label}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.im_filter = label
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Load influencers
    f = st.session_state.im_filter
    status_param = None if f == "All" else f.lower()
    rows = db.get_influencers(status=status_param)

    if not rows:
        msg = (
            "Your watchlist is empty. Add influencers to start monitoring their posts."
            if f == "All"
            else f"No {f.lower()} influencers."
        )
        st.markdown(f"<div class='empty-state'>{msg}</div>", unsafe_allow_html=True)
        return

    # Table header
    st.markdown(
        "<div style='display:flex;padding:6px 14px;border-bottom:2px solid #374151;"
        "font-size:0.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;gap:12px;'>"
        "<span style='flex:2;'>Name</span>"
        "<span style='flex:2;'>Handle</span>"
        "<span style='flex:1;'>Niche</span>"
        "<span style='flex:1;'>Status</span>"
        "<span style='flex:1;'>Comments</span>"
        "<span style='flex:1;'>&nbsp;</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    for row in rows:
        row_id         = row["id"]
        name           = row["name"]
        handle         = row.get("linkedin_handle") or row.get("handle") or ""
        url            = f"https://www.linkedin.com/in/{handle}/" if handle else "#"
        niche          = row.get("niche") or ""
        status         = row.get("status") or "active"
        comments_posted = int(row.get("comments_posted") or 0)

        # Check if this row is pending remove confirmation
        if st.session_state.im_remove_confirm == row_id:
            st.warning(
                f"Remove **{name}** from watchlist? The comment agent will stop monitoring their posts."
            )
            conf_col, cancel_col, _ = st.columns([1, 1, 4])
            with conf_col:
                if st.button("Confirm Remove", key=f"im_confirm_{row_id}", type="primary"):
                    db.delete_influencer(row_id)
                    st.session_state.im_remove_confirm = None
                    st.toast(f"Removed {name}", icon="🗑️")
                    st.rerun()
            with cancel_col:
                if st.button("Cancel", key=f"im_cancelrem_{row_id}"):
                    st.session_state.im_remove_confirm = None
                    st.rerun()
            continue

        col_name, col_handle, col_niche, col_status, col_comments, col_actions = st.columns([2, 2, 1, 1, 1, 1])
        with col_name:
            st.markdown(
                f"<div style='font-size:0.88rem;font-weight:700;color:#FAFAFA;"
                f"padding:6px 0;'>{name}</div>",
                unsafe_allow_html=True,
            )
        with col_handle:
            st.markdown(
                f"<div style='padding:6px 0;font-size:0.82rem;'>"
                f"<a href='{url}' target='_blank' style='color:#0A66C2;text-decoration:none;'>"
                f"@{handle or '—'}</a></div>",
                unsafe_allow_html=True,
            )
        with col_niche:
            st.markdown(
                f"<div style='padding:6px 0;'>{_niche_pill(niche)}</div>",
                unsafe_allow_html=True,
            )
        with col_status:
            st.markdown(
                f"<div style='padding:6px 0;'>{_status_pill(status)}</div>",
                unsafe_allow_html=True,
            )
        with col_comments:
            st.markdown(
                f"<div style='padding:6px 0;'>"
                f"<span style='background:#2D3748;color:#9AA0B2;padding:2px 8px;"
                f"border-radius:10px;font-size:0.72rem;'>{comments_posted} comments</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with col_actions:
            btn_a, btn_b = st.columns(2)
            with btn_a:
                if status == "active":
                    if st.button("💤", key=f"im_hib_{row_id}", help="Hibernate", use_container_width=True):
                        db.hibernate_influencer(row_id)
                        st.toast(f"{name} hibernated")
                        st.rerun()
                else:
                    if st.button("▶", key=f"im_act_{row_id}", help="Activate", use_container_width=True):
                        db.activate_influencer(row_id)
                        st.toast(f"{name} activated")
                        st.rerun()
            with btn_b:
                if st.button("✕", key=f"im_rem_{row_id}", help="Remove", use_container_width=True):
                    st.session_state.im_remove_confirm = row_id
                    st.rerun()


# ── Discover tab ──────────────────────────────────────────────────────────────

def _render_discover() -> None:
    st.markdown(
        "<div class='section-header'>Discover</div>"
        "<div style='font-size:0.82rem;color:#6B7280;margin-top:-6px;margin-bottom:14px;'>"
        "AI-powered recommendations based on your network and focus areas.</div>",
        unsafe_allow_html=True,
    )

    # Pattern card (only after 10+ signals)
    pattern_data = db.get_discover_pattern()
    pattern_text = pattern_data.get("pattern")
    signal_count = pattern_data.get("signal_count", 0)
    if pattern_text:
        st.markdown(
            f"<div class='pattern-card'>"
            f"<strong>Based on your choices:</strong> {pattern_text}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Load suggestions
    suggestions = db.get_discover_suggestions()

    if not suggestions:
        st.markdown(
            "<div class='empty-state'>Generating suggestions…</div>",
            unsafe_allow_html=True,
        )
        with st.spinner("Calling Claude…"):
            db.trigger_discover_generate()
        st.rerun()
        return

    for s in suggestions:
        sid     = s["id"]
        name    = s.get("name") or "Unknown"
        handle  = s.get("linkedin_handle") or ""
        headline = s.get("headline") or ""
        niche   = s.get("niche") or ""
        reason  = s.get("reason") or ""

        st.markdown(
            f"<div class='discover-card'>"
            f"<div class='discover-name'>{name}</div>"
            f"<div class='discover-headline'>{headline}</div>"
            f"{_niche_pill(niche)}"
            f"<div class='discover-reason' style='margin-top:8px;'>{reason}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        btn_l, btn_r, _ = st.columns([1, 1, 4])
        with btn_l:
            if st.button(
                "🔗 Connect",
                key=f"disc_accept_{sid}",
                type="primary",
                use_container_width=True,
                help="Adds to your connection queue",
            ):
                db.accept_discover_suggestion(sid)
                st.toast(f"Added {name} to connection queue")
                st.rerun()
        with btn_r:
            if st.button(
                "Not for me",
                key=f"disc_dismiss_{sid}",
                use_container_width=True,
            ):
                db.dismiss_discover_suggestion(sid)
                st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Refresh button
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Suggestions", key="disc_refresh"):
        with st.spinner("Generating new suggestions…"):
            db.trigger_discover_generate()
        st.toast("New suggestions generating…")
        st.rerun()


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    _init_im_states()

    st.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
        "Influencer Manager</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:16px;'>"
        "Track and grow your network of financial crime thought leaders.</div>",
        unsafe_allow_html=True,
    )

    # Tab navigation
    tab_l, tab_r, _ = st.columns([1, 1, 4])
    with tab_l:
        if st.button(
            "📋  Watchlist",
            key="im_tab_watchlist",
            type="primary" if st.session_state.im_tab == 0 else "secondary",
            use_container_width=True,
        ):
            st.session_state.im_tab = 0
            st.rerun()
    with tab_r:
        if st.button(
            "✨  Discover",
            key="im_tab_discover",
            type="primary" if st.session_state.im_tab == 1 else "secondary",
            use_container_width=True,
        ):
            st.session_state.im_tab = 1
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.session_state.im_tab == 0:
        _render_watchlist()
    else:
        _render_discover()
