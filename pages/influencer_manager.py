"""
Influencer Manager — 3-column card grid with sidebar filters.
"""

import streamlit as st
import db

_ALL_NICHES = ["AML", "KYC", "Fraud", "Sanctions", "RegTech"]
_ALL_RELATIONSHIPS = ["Cold", "Warm", "Connected", "Partner"]

_NICHE_COLORS = {
    "AML":       "#0A66C2",
    "Fraud":     "#CC1016",
    "KYC":       "#057642",
    "Sanctions": "#E85D04",
    "RegTech":   "#7B2D8B",
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
    height: 100%;
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

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🤝 Influencer Filters")

        search = st.text_input("🔍 Search name or handle", placeholder="e.g. Kieran, AML…")

        niche_filter = st.multiselect(
            "Niche",
            options=_ALL_NICHES,
            default=[],
            placeholder="All niches",
        )

        rel_filter = st.multiselect(
            "Relationship",
            options=_ALL_RELATIONSHIPS,
            default=[],
            placeholder="All stages",
        )

        st.markdown("---")
        st.markdown("### ➕ Add Influencer")

        with st.form("add_inf_form"):
            new_name = st.text_input("Full Name *")
            new_handle = st.text_input("LinkedIn Handle *", placeholder="e.g. kieranbeer")
            new_niche = st.selectbox("Niche", _ALL_NICHES)
            new_followers = st.number_input("Followers", min_value=0, value=0, step=500)
            new_rel = st.selectbox("Relationship", _ALL_RELATIONSHIPS)
            submitted = st.form_submit_button("Add", use_container_width=True)
            if submitted:
                if not new_name or not new_handle:
                    st.error("Name and handle are required.")
                else:
                    url = f"https://www.linkedin.com/in/{new_handle.lstrip('@')}/"
                    db.add_influencer(
                        new_name,
                        url,
                        new_handle.lstrip("@"),
                        new_niche,
                        int(new_followers),
                        new_rel,
                    )
                    st.success(f"Added {new_name}!")
                    st.rerun()

    # ── Main content ───────────────────────────────────────────────────────────
    rows = db.get_influencers(
        search=search or None,
        niches=niche_filter or None,
        relationships=rel_filter or None,
    )

    total = len(rows)
    st.markdown(
        f"<div style='color:#9AA0B2;font-size:0.82rem;margin-bottom:16px;'>{total} influencer{'s' if total != 1 else ''} found</div>",
        unsafe_allow_html=True,
    )

    if not rows:
        st.markdown('<div class="empty-state">No influencers match your filters.</div>', unsafe_allow_html=True)
        return

    # 3-column card grid
    COLS = 3
    for row_start in range(0, len(rows), COLS):
        chunk = rows[row_start: row_start + COLS]
        cols = st.columns(COLS)

        for col, row in zip(cols, chunk):
            row_id = row["id"]
            name = row["name"]
            handle = row.get("handle") or ""
            url = row.get("linkedin_url") or (f"https://www.linkedin.com/in/{handle}/" if handle else "#")
            niche = row.get("niche") or "—"
            rel = row.get("relationship") or "Cold"
            followers = row.get("follower_count") or 0
            last = row.get("last_interacted")
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

                # Relationship update
                new_rel = st.selectbox(
                    "Stage",
                    _ALL_RELATIONSHIPS,
                    index=_ALL_RELATIONSHIPS.index(rel) if rel in _ALL_RELATIONSHIPS else 0,
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
