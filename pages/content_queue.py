"""
Content Queue page — Draft / Scheduled / Posted sub-tabs.
"""

import streamlit as st
import db


_STATUS_COLORS = {
    "draft":     "#F5A623",
    "scheduled": "#0A66C2",
    "posted":    "#2ECC71",
}

_CARD_CSS = """
<style>
.post-card {
    background: #1E2130;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
    border-left: 4px solid {color};
}
.post-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 6px;
}
.post-card-body {
    font-size: 0.85rem;
    color: #C0C4D0;
    line-height: 1.55;
    white-space: pre-wrap;
    margin-bottom: 10px;
}
.post-card-meta {
    font-size: 0.75rem;
    color: #6B7280;
}
.status-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #fff;
    background: {color};
    margin-right: 8px;
}
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.9rem;
    padding: 48px 0;
}
</style>
"""


def _badge(status: str) -> str:
    color = _STATUS_COLORS.get(status, "#555")
    return f'<span class="status-badge" style="background:{color};">{status.upper()}</span>'


def _render_cards(rows: list[dict]) -> None:
    if not rows:
        st.markdown('<div class="empty-state">Nothing here yet — the agent will populate this queue automatically.</div>', unsafe_allow_html=True)
        return

    for row in rows:
        color = _STATUS_COLORS.get(row["status"], "#555")
        status = row["status"]
        row_id = row["id"]
        title = row.get("title") or "Untitled"
        body = row.get("body") or ""
        created = row.get("created_at", "")[:16]

        st.markdown(
            _CARD_CSS.format(color=color)
            + f"""
            <div class="post-card" style="border-left-color:{color}">
                <div class="post-card-title">{title}</div>
                <div class="post-card-body">{body[:400]}{"…" if len(body) > 400 else ""}</div>
                <div class="post-card-meta">{_badge(status)} Created {created}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b, col_c, col_spacer = st.columns([1, 1, 1, 5])

        with col_a:
            if status == "draft":
                if st.button("✅ Approve", key=f"cq_approve_{row_id}"):
                    db.update_content_status(row_id, "scheduled")
                    st.rerun()
            elif status == "scheduled":
                if st.button("📤 Mark Posted", key=f"cq_post_{row_id}"):
                    db.update_content_status(row_id, "posted")
                    st.rerun()

        with col_b:
            if st.button("✏️ Edit", key=f"cq_edit_{row_id}"):
                st.session_state[f"editing_{row_id}"] = True

        with col_c:
            if st.button("🗑️ Delete", key=f"cq_delete_{row_id}"):
                db.delete_content(row_id)
                st.rerun()

        # Inline edit form
        if st.session_state.get(f"editing_{row_id}"):
            with st.form(key=f"edit_form_{row_id}"):
                new_body = st.text_area("Edit post body", value=body, height=180)
                save, cancel = st.columns(2)
                with save:
                    if st.form_submit_button("💾 Save"):
                        db.update_content_body(row_id, new_body)
                        st.session_state[f"editing_{row_id}"] = False
                        st.rerun()
                with cancel:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"editing_{row_id}"] = False
                        st.rerun()

        st.markdown("<hr style='border-color:#2C3045;margin:4px 0 16px 0;'>", unsafe_allow_html=True)


def render() -> None:
    st.markdown("### Content Queue")
    sub1, sub2, sub3 = st.tabs(["🟡  Drafts", "🔵  Scheduled", "🟢  Posted"])

    with sub1:
        _render_cards(db.get_content_queue("draft"))

    with sub2:
        _render_cards(db.get_content_queue("scheduled"))

    with sub3:
        _render_cards(db.get_content_queue("posted"))
