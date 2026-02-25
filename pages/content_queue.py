"""
Content Queue page — LinkedIn post cards with approval flow.
4 tabs: Drafts | Scheduled | Posted | Ignored
"""

import re
import requests as _requests
import streamlit as st
from datetime import datetime, timedelta
import db

_NICHE_KEYWORDS = {
    "AML": ["aml", "anti-money", "money laundering", "bsa", "suspicious", "sar"],
    "Fraud": ["fraud", "scam", "synthetic", "identity theft", "mule"],
    "KYC": ["kyc", "know your customer", "onboarding", "verification", "cdd"],
    "Sanctions": ["sanctions", "ofac", "sdn", "compliance", "prohibited"],
    "RegTech": ["regtech", "regulation", "fincen", "compliance tech", "ai", "model"],
    "Crypto": ["crypto", "blockchain", "defi", "digital asset", "bitcoin", "ethereum"],
}

_NICHE_COLORS = {
    "AML":       "#0A66C2",
    "Fraud":     "#CC1016",
    "KYC":       "#057642",
    "Sanctions": "#E85D04",
    "RegTech":   "#7B2D8B",
    "Crypto":    "#F39C12",
}

_CSS = """
<style>
.post-card {
    background: #1E2130;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 6px;
    border: 1px solid #2D3748;
    box-shadow: 0 1px 4px rgba(0,0,0,0.35);
}
.post-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.post-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #0A66C2;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 1.1rem;
    color: #fff;
}
.post-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}
.post-profile-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #FAFAFA;
}
.post-profile-sub {
    font-size: 0.75rem;
    color: #9AA0B2;
}
.post-body {
    font-size: 0.88rem;
    color: #D0D4E0;
    line-height: 1.6;
    white-space: pre-wrap;
    margin-bottom: 14px;
}
.post-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 6px;
}
.niche-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.70rem;
    font-weight: 700;
    color: #fff;
}
.char-badge {
    font-size: 0.72rem;
    padding: 2px 10px;
    border-radius: 20px;
    font-weight: 600;
}
.char-ok   { background: #1A2A1A; color: #6B9B6B; }
.char-warn { background: #2A2000; color: #F5A623; }
.char-over { background: #2A0000; color: #CC1016; }
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.9rem;
    padding: 60px 0 40px;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 10px; }
</style>
"""


def _extract_topic(title: str, body: str) -> str:
    text = (title + " " + body).lower()
    for niche, kws in _NICHE_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return niche
    return "FinCrime"


def _char_badge(n: int) -> str:
    if n > 3000:
        cls, note = "char-over", f"{n}/3000 ⚠ Over limit"
    elif n > 2500:
        cls, note = "char-warn", f"{n}/3000 — Near limit"
    else:
        cls, note = "char-ok", f"{n}/3000"
    return f'<span class="char-badge {cls}">{note}</span>'


def _niche_pill(niche: str) -> str:
    color = _NICHE_COLORS.get(niche, "#555")
    return f'<span class="niche-pill" style="background:{color};">{niche}</span>'


def _avatar_html(pic_url: str, name: str, title: str) -> str:
    if pic_url:
        return (
            f'<div class="post-avatar"><img src="{pic_url}" alt="profile"/></div>'
            f'<div><div class="post-profile-name">{name}</div>'
            f'<div class="post-profile-sub">{title}</div></div>'
        )
    return (
        f'<div class="post-avatar">in</div>'
        f'<div><div class="post-profile-name">{name or "Your Profile"}</div>'
        f'<div class="post-profile-sub">{title or "Connect LinkedIn to show your profile"}</div></div>'
    )


def _generate_time_slots() -> list[tuple[str, str]]:
    """Generate scheduling slots: next even hour, then every 2h up to 12h from now."""
    now = datetime.utcnow()
    hour = now.hour
    if now.minute > 0 or now.second > 0:
        hour += 1
    if hour % 2 != 0:
        hour += 1
    base = now.replace(minute=0, second=0, microsecond=0)
    base = base.replace(hour=0) + timedelta(hours=hour)

    slots = []
    for step in range(6):
        slot_dt = base + timedelta(hours=step * 2)
        delta = (slot_dt - now).total_seconds()
        if delta < 30 * 60:
            continue
        if delta > 12 * 3600:
            break
        local_dt = slot_dt - timedelta(hours=5)
        hour_12 = local_dt.hour % 12 or 12
        ampm = "AM" if local_dt.hour < 12 else "PM"
        now_local = now - timedelta(hours=5)
        if local_dt.date() == now_local.date():
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
    local_dt = dt - timedelta(hours=5)
    now_local = datetime.utcnow() - timedelta(hours=5)
    hour_12 = local_dt.hour % 12 or 12
    ampm = "AM" if local_dt.hour < 12 else "PM"
    if local_dt.date() == now_local.date():
        return f"Today at {hour_12}:00 {ampm} ET"
    return f"Tomorrow at {hour_12}:00 {ampm} ET"


def _render_draft_cards(rows: list[dict], api_url: str) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">📭</div>'
            'Nothing here yet — the research agent runs every 4 hours<br>'
            'and will populate this automatically.</div>',
            unsafe_allow_html=True,
        )
        return

    pic_url       = st.session_state.get("linkedin_profile_picture_url") or ""
    profile_name  = st.session_state.get("linkedin_profile_name") or ""
    profile_title = st.session_state.get("linkedin_profile_title") or ""

    for row in rows:
        row_id     = row["id"]
        title      = row.get("title") or "Untitled"
        body       = row.get("body") or ""
        created    = row.get("created_at", "")[:16]
        char_count = len(body)
        topic      = _extract_topic(title, body)

        avatar_html = _avatar_html(pic_url, profile_name, profile_title)

        st.markdown(
            f"""
            <div class="post-card">
                <div class="post-card-header">
                    {avatar_html}
                </div>
                <div class="post-body">{body[:600]}{"…" if len(body) > 600 else ""}</div>
                <div class="post-footer">
                    <div>{_niche_pill(topic)}</div>
                    <div>
                        {_char_badge(char_count)}
                        &nbsp;<span style="font-size:0.72rem;color:#6B7280;">{created}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        scheduling_this = st.session_state.get("cq_scheduling_id") == row_id
        confirming_delete = st.session_state.get(f"cq_confirm_delete_{row_id}", False)

        btn1, btn2, btn3, btn4, _spacer = st.columns([1.3, 1.2, 1, 0.6, 3])

        with btn1:
            if st.button("📤 Post Now", key=f"cq_postnow_{row_id}", type="primary"):
                if not st.session_state.get("linkedin_access_token"):
                    st.warning("Connect LinkedIn to post directly.")
                else:
                    try:
                        r    = _requests.post(f"{api_url}/posts/{row_id}/publish", timeout=15)
                        data = r.json()
                        if data.get("ok"):
                            db.update_content_status(row_id, "posted")
                            li_id = data.get("linkedin_post_id", "")
                            st.toast(f"✅ Posted to LinkedIn!{' ID: ' + li_id if li_id else ''}")
                            st.rerun()
                        else:
                            st.error(data.get("error", "Publish failed"))
                    except Exception as e:
                        st.error(f"Error: {e}")

        with btn2:
            sched_label = "⏰ Cancel" if scheduling_this else "⏰ Schedule"
            if st.button(sched_label, key=f"cq_sched_btn_{row_id}"):
                if scheduling_this:
                    st.session_state.pop("cq_scheduling_id", None)
                else:
                    st.session_state["cq_scheduling_id"] = row_id
                    st.session_state.pop(f"cq_editing_{row_id}", None)
                st.rerun()

        with btn3:
            if st.button("✏️ Edit", key=f"cq_edit_{row_id}"):
                st.session_state[f"cq_editing_{row_id}"] = not st.session_state.get(
                    f"cq_editing_{row_id}", False
                )
                st.session_state.pop("cq_scheduling_id", None)
                st.rerun()

        with btn4:
            if not confirming_delete:
                if st.button("🗑️", key=f"cq_delete_{row_id}", help="Delete post"):
                    st.session_state[f"cq_confirm_delete_{row_id}"] = True
                    st.rerun()
            else:
                if st.button("Confirm", key=f"cq_delete_confirm_{row_id}", type="primary"):
                    r = _requests.delete(f"{api_url}/posts/{row_id}", timeout=5)
                    db.delete_content(row_id)
                    st.session_state.pop(f"cq_confirm_delete_{row_id}", None)
                    st.rerun()

        # Delete confirmation prompt
        if confirming_delete:
            c1, c2, _ = st.columns([1, 1, 5])
            with c1:
                st.warning("Delete this post?")
            with c2:
                if st.button("Cancel", key=f"cq_delete_cancel_{row_id}"):
                    st.session_state.pop(f"cq_confirm_delete_{row_id}", None)
                    st.rerun()

        # Inline scheduler
        if scheduling_this:
            slots = _generate_time_slots()
            if not slots:
                st.warning("No scheduling slots available in the next 12 hours.")
            else:
                with st.form(key=f"cq_sched_form_{row_id}"):
                    slot_labels = [s[0] for s in slots]
                    slot_isos   = [s[1] for s in slots]
                    choice_idx = st.selectbox(
                        "Publish at:",
                        range(len(slot_labels)),
                        format_func=lambda i: slot_labels[i],
                        key=f"cq_slot_select_{row_id}",
                    )
                    sc, cc = st.columns(2)
                    with sc:
                        if st.form_submit_button("Confirm Schedule", use_container_width=True, type="primary"):
                            result = db.schedule_post(row_id, slot_isos[choice_idx])
                            if result.get("ok"):
                                st.session_state.pop("cq_scheduling_id", None)
                                st.toast(f"⏰ Scheduled: {slot_labels[choice_idx]}")
                                st.rerun()
                            else:
                                st.error(result.get("error", "Failed to schedule"))
                    with cc:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.pop("cq_scheduling_id", None)
                            st.rerun()

        # Inline edit form
        if st.session_state.get(f"cq_editing_{row_id}"):
            with st.form(key=f"cq_edit_form_{row_id}"):
                new_body = st.text_area("Edit post", value=body, height=200)
                if len(new_body) > 3000:
                    st.warning(f"⚠️ {len(new_body)} chars — over LinkedIn 3000 char limit")
                elif len(new_body) > 2500:
                    st.warning(f"⚠️ {len(new_body)} chars — approaching limit")
                sc, cc = st.columns(2)
                with sc:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        db.update_content_body(row_id, new_body)
                        st.session_state[f"cq_editing_{row_id}"] = False
                        st.toast("✅ Post updated")
                        st.rerun()
                with cc:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state[f"cq_editing_{row_id}"] = False
                        st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def _render_scheduled_rows(rows: list[dict], api_url: str) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">⏰</div>No scheduled posts</div>',
            unsafe_allow_html=True,
        )
        return

    st.info("Scheduled posts publish automatically at the scheduled time.")

    # Table header
    st.markdown(
        "<div style='display:flex;padding:6px 0;border-bottom:2px solid #374151;"
        "font-size:0.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;gap:12px;'>"
        "<span style='flex:1.5;'>Topic</span>"
        "<span style='flex:5;'>Post</span>"
        "<span style='flex:2;'>Scheduled For</span>"
        "<span style='flex:1;'>Action</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    for row in rows:
        row_id       = row["id"]
        title        = row.get("title") or ""
        body         = row.get("body") or ""
        scheduled_at = row.get("scheduled_at") or ""
        topic        = _extract_topic(title, body)
        truncated    = body[:100] + ("…" if len(body) > 100 else "")
        time_label   = _format_scheduled_time(scheduled_at)

        col_info, col_btn = st.columns([10, 1.5])
        with col_info:
            st.markdown(
                f"<div style='display:flex;align-items:center;padding:9px 0;"
                f"border-bottom:1px solid #2D3748;gap:12px;'>"
                f"<span style='flex:1.5;'>{_niche_pill(topic)}</span>"
                f"<span style='flex:5;font-size:0.83rem;color:#9AA0B2;'>{truncated}</span>"
                f"<span style='flex:2;font-size:0.78rem;color:#F59E0B;font-weight:600;'>{time_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with col_btn:
            if st.button("Cancel", key=f"cq_sched_cancel_{row_id}", help="Return to drafts"):
                db.update_content_status(row_id, "draft")
                st.rerun()


def _render_posted_rows(rows: list[dict]) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">📭</div>No posted content yet</div>',
            unsafe_allow_html=True,
        )
        return

    # Table header
    st.markdown(
        "<div style='display:flex;padding:6px 0;border-bottom:2px solid #374151;"
        "font-size:0.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;gap:12px;'>"
        "<span style='flex:1.5;'>Topic</span>"
        "<span style='flex:5;'>Post</span>"
        "<span style='flex:1.5;'>Posted</span>"
        "<span style='flex:1;'>Link</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    for row in rows:
        title     = row.get("title") or ""
        body      = row.get("body") or ""
        posted_at = (row.get("posted_at") or row.get("created_at") or "")[:16]
        topic     = _extract_topic(title, body)
        truncated = body[:100] + ("…" if len(body) > 100 else "")

        # No LinkedIn post URL stored for content_queue — show dash
        st.markdown(
            f"<div style='display:flex;align-items:center;padding:9px 0;"
            f"border-bottom:1px solid #2D3748;gap:12px;'>"
            f"<span style='flex:1.5;'>{_niche_pill(topic)}</span>"
            f"<span style='flex:5;font-size:0.83rem;color:#9AA0B2;'>{truncated}</span>"
            f"<span style='flex:1.5;font-size:0.75rem;color:#6B7280;'>{posted_at}</span>"
            f"<span style='flex:1;font-size:0.75rem;color:#4B5563;'>—</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_ignored_rows(rows: list[dict]) -> None:
    if not rows:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">🚫</div>No ignored posts</div>',
            unsafe_allow_html=True,
        )
        return

    for row in rows:
        title     = row.get("title") or ""
        body      = row.get("body") or ""
        created   = (row.get("created_at") or "")[:16]
        topic     = _extract_topic(title, body)
        truncated = body[:100] + ("…" if len(body) > 100 else "")

        st.markdown(
            f"<div style='display:flex;align-items:center;padding:9px 0;"
            f"border-bottom:1px solid #2D3748;gap:12px;color:#4B5563;'>"
            f"<span style='flex:1.5;'>{_niche_pill(topic)}</span>"
            f"<span style='flex:5;font-size:0.83rem;'>{truncated}</span>"
            f"<span style='flex:1.5;font-size:0.75rem;'>{created}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render(api_url: str = "http://localhost:8000") -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    all_rows  = db.get_content_queue()
    drafts    = [r for r in all_rows if r["status"] in ("draft", "draft_saved", "pending")]
    scheduled = [r for r in all_rows if r["status"] == "scheduled"]
    posted    = [r for r in all_rows if r["status"] == "posted"]
    ignored   = [r for r in all_rows if r["status"] in ("archived", "ignored")]

    # ── Filter chips ───────────────────────────────────────────────────────────
    if "cq_filter" not in st.session_state:
        st.session_state.cq_filter = "drafts"

    filters = [
        ("drafts",    f"Drafts ({len(drafts)})"       if drafts    else "Drafts"),
        ("scheduled", f"Scheduled ({len(scheduled)})" if scheduled else "Scheduled"),
        ("posted",    f"Posted ({len(posted)})"        if posted    else "Posted"),
        ("ignored",   f"Ignored ({len(ignored)})"     if ignored   else "Ignored"),
    ]

    f1, f2, f3, f4, _ = st.columns([1, 1.2, 1, 1, 2])
    for col, (filt, label) in zip([f1, f2, f3, f4], filters):
        with col:
            is_active = st.session_state.cq_filter == filt
            if st.button(
                label,
                key=f"cq_chip_{filt}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.cq_filter = filt
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    active_filter = st.session_state.cq_filter

    if active_filter == "drafts":
        _render_draft_cards(drafts, api_url)
    elif active_filter == "scheduled":
        _render_scheduled_rows(scheduled, api_url)
    elif active_filter == "posted":
        _render_posted_rows(posted)
    elif active_filter == "ignored":
        _render_ignored_rows(ignored)
