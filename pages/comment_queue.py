"""
Comment Queue page — pending inbox with approve / schedule / edit / ignore actions.
"""

import re
import requests as _requests
import streamlit as st
from datetime import datetime, timedelta, timezone
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


def _generate_time_slots() -> list[tuple[str, str]]:
    """Generate scheduling slots: next even hour, then every 2h up to 12h from now."""
    now = datetime.utcnow()
    # Round up to next even hour
    hour = now.hour
    if now.minute > 0 or now.second > 0:
        hour += 1
    if hour % 2 != 0:
        hour += 1
    # Build base: today at `hour`, forward
    base = now.replace(minute=0, second=0, microsecond=0)
    base = base.replace(hour=0) + timedelta(hours=hour)

    slots = []
    for step in range(6):  # 0,2,4,6,8,10 hours from base → up to 10h after base
        slot_dt = base + timedelta(hours=step * 2)
        delta = (slot_dt - now).total_seconds()
        if delta < 30 * 60:
            continue  # must be ≥ 30 min from now
        if delta > 12 * 3600:
            break
        # Display in ET (UTC-5 rough approximation — keep simple)
        local_dt = slot_dt - timedelta(hours=5)
        hour_12 = local_dt.hour % 12 or 12
        ampm = "AM" if local_dt.hour < 12 else "PM"
        if local_dt.date() == (now - timedelta(hours=5)).date():
            label = f"Today at {hour_12}:00 {ampm} ET"
        else:
            label = f"Tomorrow at {hour_12}:00 {ampm} ET"
        iso = slot_dt.strftime("%Y-%m-%dT%H:%M:%S")
        slots.append((label, iso))

    return slots


def _format_scheduled_time(iso_str: str) -> str:
    """Format a UTC ISO datetime string as 'Today at 5:00 PM ET'."""
    if not iso_str:
        return ""
    try:
        dt = datetime.strptime(iso_str[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            dt = datetime.strptime(iso_str[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return iso_str
    local_dt = dt - timedelta(hours=5)  # rough ET
    now_local = datetime.utcnow() - timedelta(hours=5)
    hour_12 = local_dt.hour % 12 or 12
    ampm = "AM" if local_dt.hour < 12 else "PM"
    if local_dt.date() == now_local.date():
        return f"Today at {hour_12}:00 {ampm} ET"
    return f"Tomorrow at {hour_12}:00 {ampm} ET"


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
        inits = "?" if inf_name in ("", "Influencer") else _initials(inf_name)
        st.markdown(
            f'<div class="group-label">{inf_name} — {len(group_rows)} draft{"s" if len(group_rows) != 1 else ""}</div>',
            unsafe_allow_html=True,
        )

        for row in group_rows:
            row_id       = row["id"]
            post_url     = row.get("post_url") or ""
            post_content = row.get("post_content") or row.get("post_snippet") or ""
            comment_text = row.get("comment_text") or ""
            created      = row.get("created_at", "")[:16]

            # View original post link — only shown for real https:// URLs
            if post_url.startswith("https://"):
                post_link_html = (
                    '<div style="margin-bottom:8px;">'
                    f'<a href="{post_url}" target="_blank" rel="noopener noreferrer" '
                    'style="font-size:0.78rem;color:#0A66C2;text-decoration:none;">'
                    'View original post →</a></div>'
                )
            else:
                post_link_html = ""

            # "Commenting on:" post context block
            if post_content:
                ctx_text = post_content[:200] + ("..." if len(post_content) > 200 else "")
                post_context_html = (
                    '<div style="font-size:0.75rem;color:#6B7280;margin-bottom:4px;">Commenting on:</div>'
                    f'<div style="background:#161825;border-left:3px solid #0A66C2;'
                    f'border-radius:0 4px 4px 0;padding:8px 12px;font-size:0.8rem;'
                    f'color:#9AA0B2;line-height:1.5;margin-bottom:10px;">{ctx_text}</div>'
                )
            else:
                post_context_html = (
                    '<div style="font-size:0.75rem;color:#6B7280;margin-bottom:4px;">Commenting on:</div>'
                    '<div style="background:#161825;border-left:3px solid #2D3748;'
                    'border-radius:0 4px 4px 0;padding:8px 12px;font-size:0.8rem;'
                    'color:#4B5563;font-style:italic;line-height:1.5;margin-bottom:10px;">'
                    'Post content unavailable — view original post for context</div>'
                )

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

            btn1, btn2, btn3, btn4, _spacer = st.columns([1.3, 1.1, 1, 1, 3])

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
                scheduling_this = st.session_state.get("scheduling_comment_id") == row_id
                label = "⏰ Cancel Schedule" if scheduling_this else "⏰ Schedule"
                if st.button(label, key=f"cm_schedule_btn_{row_id}"):
                    if scheduling_this:
                        st.session_state.pop("scheduling_comment_id", None)
                    else:
                        st.session_state["scheduling_comment_id"] = row_id
                        st.session_state.pop(f"cm_editing_{row_id}", None)
                    st.rerun()

            with btn3:
                if st.button("✏️ Edit", key=f"cm_edit_{row_id}"):
                    st.session_state[f"cm_editing_{row_id}"] = not st.session_state.get(
                        f"cm_editing_{row_id}", False
                    )
                    st.session_state.pop("scheduling_comment_id", None)
                    st.rerun()

            with btn4:
                if st.button("🚫 Ignore", key=f"cm_ignore_{row_id}"):
                    _api("post", f"/comments/{row_id}/ignore", api_url)
                    db.update_comment_status(row_id, "ignored")
                    st.rerun()

            # Inline scheduler
            if st.session_state.get("scheduling_comment_id") == row_id:
                slots = _generate_time_slots()
                if not slots:
                    st.warning("No scheduling slots available in the next 12 hours.")
                else:
                    with st.form(key=f"cm_schedule_form_{row_id}"):
                        slot_labels = [s[0] for s in slots]
                        slot_isos   = [s[1] for s in slots]
                        choice_idx = st.selectbox(
                            "Post at:",
                            range(len(slot_labels)),
                            format_func=lambda i: slot_labels[i],
                            key=f"cm_slot_select_{row_id}",
                        )
                        sc, cc = st.columns(2)
                        with sc:
                            if st.form_submit_button("Confirm Schedule", use_container_width=True, type="primary"):
                                result = db.schedule_comment(row_id, slot_isos[choice_idx])
                                if result.get("ok"):
                                    st.session_state.pop("scheduling_comment_id", None)
                                    st.toast(f"⏰ Scheduled: {slot_labels[choice_idx]}")
                                    st.rerun()
                                else:
                                    st.error(result.get("error", "Failed to schedule"))
                        with cc:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state.pop("scheduling_comment_id", None)
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


def _render_scheduled_rows(rows: list[dict], api_url: str) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">⏰</div>No scheduled comments</div>',
            unsafe_allow_html=True,
        )
        return

    st.info("Scheduled comments are posted automatically every 15 minutes.")

    # Table header
    st.markdown(
        "<div style='display:flex;padding:6px 0;border-bottom:2px solid #374151;"
        "font-size:0.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;gap:12px;'>"
        "<span style='flex:2;'>Influencer</span>"
        "<span style='flex:4;'>Comment</span>"
        "<span style='flex:2;'>Scheduled For</span>"
        "<span style='flex:1;'>Action</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    for row in rows:
        inf_name     = _extract_influencer_name(row.get("post_url", ""), row.get("influencer_name", ""))
        comment_text = row.get("comment_text") or ""
        scheduled_at = row.get("scheduled_at") or ""
        row_id       = row["id"]
        truncated    = comment_text[:80] + ("…" if len(comment_text) > 80 else "")
        time_label   = _format_scheduled_time(scheduled_at)
        inits        = "?" if inf_name in ("", "Influencer") else _initials(inf_name)

        col_info, col_btn = st.columns([10, 1.5])
        with col_info:
            st.markdown(
                f"<div style='display:flex;align-items:center;padding:9px 0;"
                f"border-bottom:1px solid #2D3748;gap:12px;'>"
                f"<span style='flex:2;font-size:0.85rem;font-weight:700;color:#FAFAFA;'>{inf_name}</span>"
                f"<span style='flex:4;font-size:0.83rem;color:#9AA0B2;'>{truncated}</span>"
                f"<span style='flex:2;font-size:0.78rem;color:#F59E0B;font-weight:600;'>{time_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with col_btn:
            if st.button("Cancel", key=f"cm_sched_cancel_{row_id}", help="Return to pending"):
                db.update_comment_status(row_id, "pending")
                st.rerun()


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

    all_rows  = db.get_comment_queue()
    pending   = [r for r in all_rows if r["status"] in ("pending", "pending_urn")]
    scheduled = [r for r in all_rows if r["status"] == "scheduled"]
    posted    = [r for r in all_rows if r["status"] == "posted"]
    ignored   = [r for r in all_rows if r["status"] == "ignored"]

    # ── Filter chips ───────────────────────────────────────────────────────────
    if "cm_filter" not in st.session_state:
        st.session_state.cm_filter = "pending"

    filters = [
        ("pending",   f"Pending ({len(pending)})"     if pending   else "Pending"),
        ("scheduled", f"Scheduled ({len(scheduled)})" if scheduled else "Scheduled"),
        ("posted",    f"Posted ({len(posted)})"        if posted    else "Posted"),
        ("ignored",   f"Ignored ({len(ignored)})"     if ignored   else "Ignored"),
    ]

    f1, f2, f3, f4, _ = st.columns([1, 1.2, 1, 1, 2])
    for col, (filt, label) in zip([f1, f2, f3, f4], filters):
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
    elif active_filter == "scheduled":
        _render_scheduled_rows(scheduled, api_url)
    elif active_filter == "posted":
        _render_posted_rows(posted)
    elif active_filter == "ignored":
        _render_ignored_rows(ignored)
