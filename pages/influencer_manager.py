"""
Influencer Manager — 3-column card grid with inline Add Influencer form.
"""

import streamlit as st
import db

_ALL_NICHES = ["AML", "KYC", "Fraud", "Sanctions", "RegTech", "AI/Agentic", "Compliance", "Regulatory"]
_ALL_RELATIONSHIPS = ["Cold", "Warm", "Partner"]
_ALL_RELATIONSHIPS_FULL = ["Cold", "Warm", "Connected", "Partner"]

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

_REL_COLORS = {
    "Cold":      "#6B7280",
    "Warm":      "#F5A623",
    "Connected": "#0A66C2",
    "Partner":   "#057642",
}

_CSS = """
<style>
.inf-card {
    background: #1E2130;
    border-radius: 8px;
    border: 1px solid #2D3748;
    padding: 16px;
    margin-bottom: 0;
    transition: border-color 0.2s;
}
.inf-card:hover { border-color: #0A66C2; }
.inf-card-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 4px;
}
.inf-card-handle {
    font-size: 0.75rem;
    color: #0A66C2;
    margin-bottom: 8px;
}
.inf-card-meta {
    font-size: 0.74rem;
    color: #9AA0B2;
    margin-top: 8px;
}
.pill {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #fff;
    margin-right: 4px;
    margin-bottom: 4px;
}
.add-form-panel {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 20px;
}
.add-form-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 16px;
}
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.9rem;
    padding: 60px 0;
}
</style>
"""


def _niche_pill(niche: str) -> str:
    color = _NICHE_COLORS.get(niche, "#555")
    return f'<span class="pill" style="background:{color};">{niche}</span>'


def _rel_pill(rel: str) -> str:
    color = _REL_COLORS.get(rel, "#555")
    return f'<span class="pill" style="background:{color};">{rel}</span>'


def _fmt_followers(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n) if n else "—"


def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Page header row ────────────────────────────────────────────────────────
    hdr_left, hdr_right = st.columns([3, 1])
    with hdr_left:
        st.markdown(
            "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
            "🤝 Influencer Manager</div>"
            "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:16px;'>"
            "Track and engage your network of financial crime thought leaders.</div>",
            unsafe_allow_html=True,
        )
    with hdr_right:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        showing = st.session_state.get("im_show_add_form", False)
        btn_label = "✕ Cancel" if showing else "➕ Add Influencer"
        if st.button(btn_label, key="im_toggle_add", type="primary", use_container_width=True):
            st.session_state["im_show_add_form"] = not showing
            st.rerun()

    # ── Inline filters ─────────────────────────────────────────────────────────
    fil1, fil2, fil3 = st.columns([2, 2, 1])
    with fil1:
        search = st.text_input("Search", placeholder="🔍 Name or handle…", label_visibility="collapsed")
    with fil2:
        niche_filter = st.multiselect("Niche", options=_ALL_NICHES, default=[], placeholder="Filter by niche", label_visibility="collapsed")
    with fil3:
        rel_filter = st.multiselect("Stage", options=_ALL_RELATIONSHIPS_FULL, default=[], placeholder="Any stage", label_visibility="collapsed")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Inline Add Influencer form ─────────────────────────────────────────────
    if st.session_state.get("im_show_add_form", False):
        st.markdown("<div class='add-form-panel'><div class='add-form-title'>New Influencer</div></div>",
                    unsafe_allow_html=True)
        with st.form("im_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_name   = st.text_input("Full Name *", placeholder="e.g. Kieran Beer")
                new_handle = st.text_input("LinkedIn Handle *", placeholder="e.g. kieranbeer  (no @)")
            with col2:
                new_niche = st.selectbox("Niche", _ALL_NICHES)
                new_rel   = st.selectbox("Relationship Stage", _ALL_RELATIONSHIPS)
            new_notes = st.text_area("Notes (optional)", placeholder="e.g. Met at ACAMS conference, strong AML perspective", height=80)

            save_col, cancel_col = st.columns([1, 1])
            with save_col:
                submitted = st.form_submit_button("💾 Save Influencer", type="primary", use_container_width=True)
            with cancel_col:
                cancelled = st.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not new_name.strip() or not new_handle.strip():
                    st.error("Full Name and LinkedIn Handle are required.")
                else:
                    handle_clean = new_handle.strip().lstrip("@")
                    url = f"https://www.linkedin.com/in/{handle_clean}/"
                    db.add_influencer(
                        name=new_name.strip(),
                        linkedin_url=url,
                        handle=handle_clean,
                        niche=new_niche,
                        follower_count=0,
                        relationship=new_rel,
                        notes=new_notes.strip(),
                    )
                    st.session_state["im_show_add_form"] = False
                    st.toast(f"✅ Influencer added: {new_name.strip()}")
                    st.rerun()
            if cancelled:
                st.session_state["im_show_add_form"] = False
                st.rerun()

    # ── Load & display grid ────────────────────────────────────────────────────
    rows = db.get_influencers(
        search=search or None,
        niches=niche_filter or None,
        relationships=rel_filter or None,
    )

    total = len(rows)
    st.markdown(
        f"<div style='color:#9AA0B2;font-size:0.82rem;margin-bottom:16px;'>"
        f"{total} influencer{'s' if total != 1 else ''} found</div>",
        unsafe_allow_html=True,
    )

    if not rows:
        st.markdown('<div class="empty-state">No influencers match your filters.</div>', unsafe_allow_html=True)
        return

    COLS = 3
    rel_options = _ALL_RELATIONSHIPS_FULL
    for row_start in range(0, len(rows), COLS):
        chunk = rows[row_start: row_start + COLS]
        cols  = st.columns(COLS)

        for col, row in zip(cols, chunk):
            row_id   = row["id"]
            name     = row["name"]
            handle   = row.get("handle") or ""
            url      = row.get("linkedin_url") or (f"https://www.linkedin.com/in/{handle}/" if handle else "#")
            niche    = row.get("niche") or "—"
            rel      = row.get("relationship") or "Cold"
            followers = row.get("follower_count") or 0
            last     = row.get("last_interacted")
            last_str = last[:10] if last else "Never"

            with col:
                st.markdown(
                    f"""
                    <div class="inf-card">
                        <div class="inf-card-name">{name}</div>
                        <div class="inf-card-handle">
                            <a href="{url}" target="_blank" style="color:#0A66C2;text-decoration:none;">
                                @{handle or '—'}
                            </a>
                        </div>
                        {_niche_pill(niche)} {_rel_pill(rel)}
                        <div class="inf-card-meta">
                            👥 {_fmt_followers(followers)} followers<br>
                            🕐 Last: {last_str}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                cur_idx = rel_options.index(rel) if rel in rel_options else 0
                new_rel = st.selectbox(
                    "Stage",
                    rel_options,
                    index=cur_idx,
                    key=f"inf_rel_{row_id}",
                    label_visibility="collapsed",
                )
                btn_a, btn_b = st.columns(2)
                with btn_a:
                    if st.button("💾", key=f"inf_save_{row_id}", help="Save relationship", use_container_width=True):
                        db.update_influencer_relationship(row_id, new_rel)
                        st.toast(f"✅ {name} → {new_rel}")
                        st.rerun()
                with btn_b:
                    if st.button("📌", key=f"inf_log_{row_id}", help="Log interaction", use_container_width=True):
                        db.log_influencer_interaction(row_id)
                        st.toast(f"📌 Interaction logged for {name}")
                        st.rerun()

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
