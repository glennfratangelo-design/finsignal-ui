"""
Comment Queue page — pending inbox with approve / edit / ignore actions.
"""

import re
import requests as _requests
import streamlit as st
import db

_CSS = """
<style>
.comment-card {
    background: #1E2130;
    border-radius: 8px;
    padding: 16px 18px;
    margin-bottom: 6px;
    border: 1px solid #2D3748;
}
.influencer-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.inf-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #0A66C2;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.88rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
}
.inf-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #FAFAFA;
}
.inf-post-link {
    font-size: 0.73rem;
    color: #0A66C2;
}
.post-snippet {
    background: #0F1117;
    border-left: 3px solid #2D3748;
    border-radius: 0 6px 6px 0;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #9AA0B2;
    font-style: italic;
    margin-bottom: 10px;
    line-height: 1.5;
}
.reply-box {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #D0D4E0;
    line-height: 1.55;
    white-space: pre-wrap;
    margin-bottom: 12px;
}
.group-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 20px 0 10px;
}
.approve-panel {
    background: #111320;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.approve-panel-title {
    font-size: 0.80rem;
    color: #9AA0B2;
    margin-bottom: 8px;
    font-weight: 600;
}
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.95rem;
    padding: 60px 0 40px;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 10px; }
</style>
"""


def _extract_influencer_name(post_url: str, fallback: str) -> str:
    if fallback:
        return fallback
    m = re.search(r"linkedin\.com/(?:posts|in)/([^/_?&#]+)", post_url or "")
    if m:
        return m.group(1).replace("-", " ").title()
    return "Influencer"


def _initials(name: str) -> str:
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()


def _api(method: str, path: str, api_url: str) -> bool:
    try:
        r = getattr(_requests, method)(f"{api_url}{path}", timeout=5)
        return r.status_code < 300
    except Exception:
        return False


def _render_cards(rows: list[dict], api_url: str) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    if not rows:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">✨</div>
                Comment inbox is clear
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Group by influencer name
    groups: dict[str, list[dict]] = {}
    for row in rows:
        inf_name = _extract_influencer_name(
            row.get("post_url", ""),
            row.get("influencer_name", ""),
        )
        groups.setdefault(inf_name, []).append(row)

    for inf_name, group_rows in groups.items():
        inits = _initials(inf_name)
        st.markdown(
            f'<div class="group-label">{inf_name} — {len(group_rows)} draft{"s" if len(group_rows) != 1 else ""}</div>',
            unsafe_allow_html=True,
        )

        for row in group_rows:
            row_id = row["id"]
            post_url = row.get("post_url") or ""
            snippet = row.get("post_snippet") or ""
            comment_text = row.get("comment_text") or ""
            created = row.get("created_at", "")[:16]

            snippet_html = (
                f'<div class="post-snippet">"{snippet[:300]}{"…" if len(snippet) > 300 else ""}"</div>'
                if snippet
                else ""
            )

            short_url = post_url.replace("https://www.", "").replace("https://", "")[:60] + ("…" if len(post_url) > 60 else "")

            st.markdown(
                f"""
                <div class="comment-card">
                    <div class="influencer-header">
                        <div class="inf-avatar">{inits}</div>
                        <div>
                            <div class="inf-name">{inf_name}</div>
                            <div class="inf-post-link">
                                <a href="{post_url}" target="_blank" style="color:#0A66C2;">{short_url}</a>
                            </div>
                        </div>
                    </div>
                    {snippet_html}
                    <div class="reply-box">{comment_text}</div>
                    <div style="font-size:0.72rem;color:#6B7280;">Drafted {created}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            showing_approve = st.session_state.get(f"cm_approving_{row_id}", False)

            btn1, btn2, btn3, btn_spacer = st.columns([1.3, 1, 1, 4])

            with btn1:
                if not showing_approve:
                    if st.button("✅ Approve & Post", key=f"cm_approve_{row_id}"):
                        st.session_state[f"cm_approving_{row_id}"] = True
                        st.rerun()
                else:
                    if st.button("✕ Cancel", key=f"cm_cancel_{row_id}"):
                        st.session_state[f"cm_approving_{row_id}"] = False
                        st.rerun()

            with btn2:
                if st.button("✏️ Edit Reply", key=f"cm_edit_{row_id}"):
                    st.session_state[f"cm_editing_{row_id}"] = not st.session_state.get(f"cm_editing_{row_id}", False)
                    st.rerun()

            with btn3:
                if st.button("🚫 Ignore", key=f"cm_ignore_{row_id}"):
                    _api("post", f"/comments/{row_id}/ignore", api_url)
                    db.update_comment_status(row_id, "ignored")
                    st.rerun()

            # Approve options panel
            if showing_approve:
                st.markdown(
                    '<div class="approve-panel"><div class="approve-panel-title">Choose action:</div></div>',
                    unsafe_allow_html=True,
                )
                opt1, opt2 = st.columns(2)
                with opt1:
                    if st.button("💬 Post Comment Now", key=f"cm_postnow_{row_id}", use_container_width=True):
                        _api("post", f"/comments/{row_id}/approve", api_url)
                        db.update_comment_status(row_id, "posted")
                        st.session_state[f"cm_approving_{row_id}"] = False
                        st.toast("✅ Comment posted")
                        st.rerun()
                with opt2:
                    if st.button("🗂️ Save for Later", key=f"cm_save_{row_id}", use_container_width=True):
                        db.update_comment_status(row_id, "saved")
                        st.session_state[f"cm_approving_{row_id}"] = False
                        st.toast("🗂️ Saved for later")
                        st.rerun()

            # Inline edit form
            if st.session_state.get(f"cm_editing_{row_id}"):
                with st.form(key=f"cm_edit_form_{row_id}"):
                    new_text = st.text_area("Edit reply", value=comment_text, height=130)
                    sc, cc = st.columns(2)
                    with sc:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            db.update_comment_text(row_id, new_text)
                            st.session_state[f"cm_editing_{row_id}"] = False
                            st.toast("✅ Reply updated")
                            st.rerun()
                    with cc:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state[f"cm_editing_{row_id}"] = False
                            st.rerun()

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


def render(api_url: str = "http://localhost:8000") -> None:
    all_rows = db.get_comment_queue()
    pending  = [r for r in all_rows if r["status"] == "pending"]
    saved    = [r for r in all_rows if r["status"] == "saved"]
    posted   = [r for r in all_rows if r["status"] == "posted"]
    ignored  = [r for r in all_rows if r["status"] == "ignored"]

    p_label = f"🟡 Pending ({len(pending)})" if pending else "🟡 Pending"
    sub1, sub2, sub3, sub4 = st.tabs([p_label, "🗂️ Saved", "🟢 Posted", "⚫ Ignored"])

    with sub1:
        _render_cards(pending, api_url)

    with sub2:
        _render_cards(saved, api_url)

    with sub3:
        _render_cards(posted, api_url)

    with sub4:
        _render_cards(ignored, api_url)
