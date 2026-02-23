"""
Comment Queue page — pending inbox with approve / edit / ignore actions.
"""

import streamlit as st
import db


_CARD_CSS = """
<style>
.comment-card {
    background: #1E2130;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #0A66C2;
}
.comment-card.ignored {
    border-left-color: #444;
    opacity: 0.55;
}
.comment-card.approved {
    border-left-color: #2ECC71;
}
.comment-url {
    font-size: 0.78rem;
    color: #0A66C2;
    margin-bottom: 6px;
    word-break: break-all;
}
.comment-text {
    font-size: 0.88rem;
    color: #D0D4E0;
    line-height: 1.55;
    white-space: pre-wrap;
    margin-bottom: 10px;
}
.comment-meta {
    font-size: 0.75rem;
    color: #6B7280;
}
.pending-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #F5A623;
    color: #fff;
    margin-right: 6px;
}
.approved-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #2ECC71;
    color: #fff;
    margin-right: 6px;
}
.ignored-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #555;
    color: #ccc;
    margin-right: 6px;
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
    cls = {"pending": "pending-badge", "approved": "approved-badge", "ignored": "ignored-badge"}.get(status, "pending-badge")
    return f'<span class="{cls}">{status.upper()}</span>'


def _render_cards(rows: list[dict]) -> None:
    if not rows:
        st.markdown('<div class="empty-state">Inbox is empty — comment suggestions will appear here after the agent runs.</div>', unsafe_allow_html=True)
        return

    for row in rows:
        status = row["status"]
        row_id = row["id"]
        post_url = row.get("post_url") or ""
        comment_text = row.get("comment_text") or ""
        created = row.get("created_at", "")[:16]

        border_extra = "ignored" if status == "ignored" else ("approved" if status == "approved" else "")
        st.markdown(
            _CARD_CSS
            + f"""
            <div class="comment-card {border_extra}">
                <div class="comment-url">🔗 {post_url}</div>
                <div class="comment-text">{comment_text[:500]}{"…" if len(comment_text) > 500 else ""}</div>
                <div class="comment-meta">{_badge(status)} Queued {created}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if status == "pending":
            col_a, col_b, col_c, col_spacer = st.columns([1.2, 1, 1, 5])

            with col_a:
                if st.button("✅ Approve & Post", key=f"cm_approve_{row_id}"):
                    db.update_comment_status(row_id, "approved")
                    st.rerun()

            with col_b:
                if st.button("✏️ Edit", key=f"cm_edit_{row_id}"):
                    st.session_state[f"cm_editing_{row_id}"] = True

            with col_c:
                if st.button("🚫 Ignore", key=f"cm_ignore_{row_id}"):
                    db.update_comment_status(row_id, "ignored")
                    st.rerun()

            # Inline edit form
            if st.session_state.get(f"cm_editing_{row_id}"):
                with st.form(key=f"cm_edit_form_{row_id}"):
                    new_text = st.text_area("Edit comment", value=comment_text, height=130)
                    save_col, cancel_col = st.columns(2)
                    with save_col:
                        if st.form_submit_button("💾 Save"):
                            db.update_comment_text(row_id, new_text)
                            st.session_state[f"cm_editing_{row_id}"] = False
                            st.rerun()
                    with cancel_col:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"cm_editing_{row_id}"] = False
                            st.rerun()

        st.markdown("<hr style='border-color:#2C3045;margin:4px 0 14px 0;'>", unsafe_allow_html=True)


def render() -> None:
    st.markdown("### Comment Queue")

    all_rows = db.get_comment_queue()
    pending = [r for r in all_rows if r["status"] == "pending"]
    approved = [r for r in all_rows if r["status"] == "approved"]
    ignored = [r for r in all_rows if r["status"] == "ignored"]

    pending_label = f"🟡  Pending ({len(pending)})" if pending else "🟡  Pending"
    sub1, sub2, sub3 = st.tabs([pending_label, "🟢  Approved", "⚫  Ignored"])

    with sub1:
        _render_cards(pending)

    with sub2:
        _render_cards(approved)

    with sub3:
        _render_cards(ignored)
