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
    margin-bottom: 10px;
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
    margin-bottom: 10px;
}
.group-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 20px 0 10px;
}
.posted-row {
    display: flex;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #2D3748;
    gap: 12px;
    font-size: 0.85rem;
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


def _api(method: str, path: str, api_url: str) -> tuple[bool, dict]:
    try:
        r = getattr(_requests, method)(f"{api_url}{path}", timeout=10)
        try:
            data = r.json()
        except Exception:
            data = {}
        return r.status_code < 300, data
    except Exception as e:
        return False, {"error": str(e)}


def _render_pending_cards(rows: list[dict], api_url: str) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">✅</div>No pending comments</div>',
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
            row_id       = row["id"]
            post_url     = row.get("post_url") or ""
            post_snippet = row.get("post_snippet") or ""
            comment_text = row.get("comment_text") or ""
            created      = row.get("created_at", "")[:16]

            # FIX 3 — View original post link
            if post_url:
                post_link_html = (
                    '<div style="margin-bottom:8px;">'
                    f'<a href="{post_url}" target="_blank" rel="noopener noreferrer" '
                    'style="font-size:0.78rem;color:#0A66C2;text-decoration:none;">'
                    'View original post →</a></div>'
                )
            else:
                post_link_html = (
                    '<div style="margin-bottom:8px;font-size:0.78rem;color:#4B5563;">'
                    'Post URL unavailable</div>'
                )

            # FIX 4 — "Commenting on:" post context block
            if post_snippet:
                ctx_text = post_snippet[:150] + ("..." if len(post_snippet) > 150 else "")
            elif post_url:
                try:
                    from urllib.parse import urlparse as _urlparse
                    ctx_text = _urlparse(post_url).netloc or "linkedin.com post"
                except Exception:
                    ctx_text = "linkedin.com post"
            else:
                ctx_text = ""

            if ctx_text:
                post_context_html = (
                    '<div style="font-size:0.75rem;color:#6B7280;margin-bottom:4px;">Commenting on:</div>'
                    f'<div style="background:#161825;border-left:3px solid #0A66C2;'
                    f'border-radius:0 4px 4px 0;padding:8px 12px;font-size:0.8rem;'
                    f'color:#9AA0B2;line-height:1.5;margin-bottom:10px;">{ctx_text}</div>'
                )
            else:
                post_context_html = ""

            st.markdown(
                f"""
                <div class="comment-card">
                    <div class="influencer-header">
                        <div class="inf-avatar">{inits}</div>
                        <div>
                            <div class="inf-name">{inf_name}</div>
                            <div style="font-size:0.72rem;color:#6B7280;">Drafted {created}</div>
                        </div>
                    </div>
                    {post_link_html}
                    {post_context_html}
                    <div class="reply-box">{comment_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn1, btn2, btn3, _spacer = st.columns([1.3, 1, 1, 4])

            with btn1:
                if st.button("✅ Approve & Post", key=f"cm_approve_{row_id}", type="primary"):
                    ok, resp = _api("post", f"/comments/{row_id}/approve", api_url)
                    if ok:
                        st.toast("✅ Comment posted to LinkedIn")
                        st.rerun()
                    else:
                        err = resp.get("error", "Unknown error")
                        st.error(f"Failed to post: {err}")

            with btn2:
                if st.button("✏️ Edit Reply", key=f"cm_edit_{row_id}"):
                    st.session_state[f"cm_editing_{row_id}"] = not st.session_state.get(
                        f"cm_editing_{row_id}", False
                    )
                    st.rerun()

            with btn3:
                if st.button("🚫 Ignore", key=f"cm_ignore_{row_id}"):
                    _api("post", f"/comments/{row_id}/ignore", api_url)
                    db.update_comment_status(row_id, "ignored")
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


def _render_posted_rows(rows: list[dict]) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">📭</div>No posted comments yet</div>',
            unsafe_allow_html=True,
        )
        return

    # Table header
    st.markdown(
        "<div style='display:flex;padding:6px 0;border-bottom:2px solid #374151;"
        "font-size:0.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;gap:12px;'>"
        "<span style='flex:2;'>Influencer</span>"
        "<span style='flex:4;'>Comment</span>"
        "<span style='flex:1.5;'>Posted</span>"
        "<span style='flex:1;'>Link</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    for row in rows:
        inf_name     = _extract_influencer_name(row.get("post_url", ""), row.get("influencer_name", ""))
        comment_text = row.get("comment_text") or ""
        post_url     = row.get("post_url") or ""
        posted_at    = (row.get("posted_at") or row.get("created_at") or "")[:16]
        truncated    = comment_text[:80] + ("…" if len(comment_text) > 80 else "")

        link_html = (
            f'<a href="{post_url}" target="_blank" '
            f'style="color:#0A66C2;text-decoration:none;font-size:0.8rem;">View post →</a>'
            if post_url
            else '<span style="color:#4B5563;font-size:0.8rem;">—</span>'
        )

        st.markdown(
            f"<div style='display:flex;align-items:center;padding:9px 0;"
            f"border-bottom:1px solid #2D3748;gap:12px;'>"
            f"<span style='flex:2;font-size:0.85rem;font-weight:700;color:#FAFAFA;'>{inf_name}</span>"
            f"<span style='flex:4;font-size:0.83rem;color:#9AA0B2;'>{truncated}</span>"
            f"<span style='flex:1.5;font-size:0.75rem;color:#6B7280;'>{posted_at}</span>"
            f"<span style='flex:1;'>{link_html}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_ignored_rows(rows: list[dict]) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">🚫</div>No ignored comments</div>',
            unsafe_allow_html=True,
        )
        return

    for row in rows:
        inf_name     = _extract_influencer_name(row.get("post_url", ""), row.get("influencer_name", ""))
        comment_text = row.get("comment_text") or ""
        created      = (row.get("created_at") or "")[:16]
        truncated    = comment_text[:80] + ("…" if len(comment_text) > 80 else "")
        st.markdown(
            f"<div style='display:flex;align-items:center;padding:9px 0;"
            f"border-bottom:1px solid #2D3748;gap:12px;color:#4B5563;'>"
            f"<span style='flex:2;font-size:0.85rem;'>{inf_name}</span>"
            f"<span style='flex:4;font-size:0.83rem;'>{truncated}</span>"
            f"<span style='flex:1.5;font-size:0.75rem;'>{created}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render(api_url: str = "http://localhost:8000") -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    all_rows = db.get_comment_queue()
    pending  = [r for r in all_rows if r["status"] in ("pending", "pending_urn")]
    posted   = [r for r in all_rows if r["status"] == "posted"]
    ignored  = [r for r in all_rows if r["status"] == "ignored"]

    # ── Filter chips ───────────────────────────────────────────────────────────
    if "cm_filter" not in st.session_state:
        st.session_state.cm_filter = "pending"

    filters = [
        ("pending", f"Pending ({len(pending)})" if pending else "Pending"),
        ("posted",  f"Posted ({len(posted)})"   if posted  else "Posted"),
        ("ignored", f"Ignored ({len(ignored)})" if ignored else "Ignored"),
    ]

    f1, f2, f3, _ = st.columns([1, 1, 1, 3])
    for col, (filt, label) in zip([f1, f2, f3], filters):
        with col:
            is_active = st.session_state.cm_filter == filt
            if st.button(
                label,
                key=f"cm_chip_{filt}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.cm_filter = filt
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    active_filter = st.session_state.cm_filter

    if active_filter == "pending":
        _render_pending_cards(pending, api_url)
    elif active_filter == "posted":
        _render_posted_rows(posted)
    elif active_filter == "ignored":
        _render_ignored_rows(ignored)
