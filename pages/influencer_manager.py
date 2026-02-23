"""
Influencer Manager page — table, search, relationship tracking, add form.
"""

import streamlit as st
import db


_RELATIONSHIP_OPTIONS = ["Cold", "Warm", "Connected", "Collaborator"]

_RELATIONSHIP_COLORS = {
    "Cold":         "#6B7280",
    "Warm":         "#F5A623",
    "Connected":    "#0A66C2",
    "Collaborator": "#2ECC71",
}

_NICHE_COLORS = {
    "Fraud":     "#E74C3C",
    "AML":       "#9B59B6",
    "KYC":       "#3498DB",
    "RegTech":   "#1ABC9C",
    "Crypto":    "#F39C12",
    "Sanctions": "#E67E22",
}

_CSS = """
<style>
.inf-card {
    background: #1E2130;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.inf-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FAFAFA;
}
.inf-url {
    font-size: 0.78rem;
    color: #0A66C2;
}
.inf-meta {
    font-size: 0.78rem;
    color: #9AA0B2;
    margin-top: 3px;
}
.niche-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.70rem;
    font-weight: 600;
    color: #fff;
    margin-right: 6px;
}
.rel-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.70rem;
    font-weight: 600;
    color: #fff;
}
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.9rem;
    padding: 48px 0;
}
</style>
"""


def _niche_badge(niche: str) -> str:
    color = _NICHE_COLORS.get(niche, "#555")
    return f'<span class="niche-badge" style="background:{color};">{niche}</span>'


def _rel_badge(rel: str) -> str:
    color = _RELATIONSHIP_COLORS.get(rel, "#555")
    return f'<span class="rel-badge" style="background:{color};">{rel}</span>'


def _fmt_followers(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def render() -> None:
    st.markdown("### Influencer Manager")
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Search bar ─────────────────────────────────────────────────────────────
    search = st.text_input("🔍 Search by name or niche", placeholder="e.g. Frank McKenna, AML…")

    rows = db.get_influencers(search=search if search else None)

    st.markdown(f"<div style='color:#9AA0B2;font-size:0.82rem;margin-bottom:12px;'>{len(rows)} influencer(s) found</div>", unsafe_allow_html=True)

    # ── Table ──────────────────────────────────────────────────────────────────
    if not rows:
        st.markdown('<div class="empty-state">No influencers match your search.</div>', unsafe_allow_html=True)
    else:
        for row in rows:
            row_id = row["id"]
            name = row["name"]
            url = row.get("linkedin_url") or ""
            niche = row.get("niche") or "—"
            followers = row.get("follower_count") or 0
            rel = row.get("relationship") or "Cold"
            last = row.get("last_interacted")
            last_str = last[:10] if last else "Never"

            col_info, col_rel, col_action = st.columns([4, 2, 2])

            with col_info:
                st.markdown(
                    f"""
                    <div class="inf-name">{name}</div>
                    <div class="inf-url"><a href="{url}" target="_blank" style="color:#0A66C2;">{url}</a></div>
                    <div class="inf-meta">
                        {_niche_badge(niche)}
                        👥 {_fmt_followers(followers)} followers &nbsp;|&nbsp; Last: {last_str}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_rel:
                st.markdown(f"<div style='padding-top:6px;'>{_rel_badge(rel)}</div>", unsafe_allow_html=True)
                new_rel = st.selectbox(
                    "Update",
                    _RELATIONSHIP_OPTIONS,
                    index=_RELATIONSHIP_OPTIONS.index(rel) if rel in _RELATIONSHIP_OPTIONS else 0,
                    key=f"inf_rel_{row_id}",
                    label_visibility="collapsed",
                )

            with col_action:
                st.markdown("<div style='padding-top:6px;'>", unsafe_allow_html=True)
                if st.button("💾 Save", key=f"inf_save_{row_id}"):
                    db.update_influencer_relationship(row_id, new_rel)
                    st.rerun()
                if st.button("📌 Log Interaction", key=f"inf_log_{row_id}"):
                    db.log_influencer_interaction(row_id)
                    st.success("Interaction logged!", icon="✅")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<hr style='border-color:#2C3045;margin:6px 0 10px 0;'>", unsafe_allow_html=True)

    # ── Add Influencer form ────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("➕ Add New Influencer"):
        with st.form("add_influencer_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Full Name *")
                new_url = st.text_input("LinkedIn URL *")
            with c2:
                new_niche = st.selectbox("Niche", ["Fraud", "AML", "KYC", "RegTech", "Crypto", "Sanctions", "Other"])
                new_followers = st.number_input("Follower Count", min_value=0, value=5000, step=500)
            new_relationship = st.selectbox("Initial Relationship", _RELATIONSHIP_OPTIONS)
            submitted = st.form_submit_button("Add Influencer")
            if submitted:
                if not new_name or not new_url:
                    st.error("Name and LinkedIn URL are required.")
                else:
                    db.add_influencer(new_name, new_url, new_niche, int(new_followers), new_relationship)
                    st.success(f"Added {new_name}!", icon="✅")
                    st.rerun()
