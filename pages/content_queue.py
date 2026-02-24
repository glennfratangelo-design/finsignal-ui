"""
Content Queue page — LinkedIn post preview cards with approval flow.
"""

import re
import requests as _requests
import streamlit as st
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

_STATUS_COLORS = {
    "draft":        "#F5A623",
    "draft_saved":  "#9AA0B2",
    "scheduled":    "#0A66C2",
    "posted":       "#057642",
}

_CSS = """
<style>
.post-card {
    background: #1E2130;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 6px;
    border: 1px solid #2D3748;
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
.status-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.70rem;
    font-weight: 700;
    color: #fff;
}
.approve-options {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.approve-title {
    font-size: 0.82rem;
    color: #9AA0B2;
    margin-bottom: 10px;
    font-weight: 600;
}
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


def _status_pill(status: str) -> str:
    color = _STATUS_COLORS.get(status, "#555")
    label = status.replace("_", " ").upper()
    return f'<span class="status-pill" style="background:{color};">{label}</span>'


def _niche_pill(niche: str) -> str:
    color = _NICHE_COLORS.get(niche, "#555")
    return f'<span class="niche-pill" style="background:{color};">{niche}</span>'


def _api(method: str, path: str, api_url: str) -> bool:
    try:
        r = getattr(_requests, method)(f"{api_url}{path}", timeout=5)
        return r.status_code < 300
    except Exception:
        return False


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


def _render_cards(rows: list[dict], api_url: str) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    if not rows:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                Nothing here yet — the research agent runs every 4 hours<br>and will populate this automatically.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    pic_url = st.session_state.get("linkedin_profile_picture_url") or ""
    profile_name = st.session_state.get("linkedin_profile_name") or ""
    profile_title = st.session_state.get("linkedin_profile_title") or ""

    for row in rows:
        status = row["status"]
        row_id = row["id"]
        title = row.get("title") or "Untitled"
        body = row.get("body") or ""
        created = row.get("created_at", "")[:16]
        char_count = len(body)
        topic = _extract_topic(title, body)

        avatar_html = _avatar_html(pic_url, profile_name, profile_title)

        st.markdown(
            f"""
            <div class="post-card">
                <div class="post-card-header">
                    {avatar_html}
                </div>
                <div class="post-body">{body[:600]}{"…" if len(body) > 600 else ""}</div>
                <div class="post-footer">
                    <div>
                        {_niche_pill(topic)}
                        &nbsp;{_status_pill(status)}
                    </div>
                    <div>
                        {_char_badge(char_count)}
                        &nbsp;<span style="font-size:0.72rem;color:#6B7280;">{created}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Action buttons
        btn_cols = st.columns([1.2, 1, 1.2, 1, 5])

        # Approve button — shows two inline options
        showing_approve = st.session_state.get(f"cq_approving_{row_id}", False)

        with btn_cols[0]:
            if status in ("draft",):
                if not showing_approve:
                    if st.button("✅ Approve", key=f"cq_approve_{row_id}"):
                        st.session_state[f"cq_approving_{row_id}"] = True
                        st.rerun()
                else:
                    if st.button("✕ Cancel", key=f"cq_cancel_approve_{row_id}"):
                        st.session_state[f"cq_approving_{row_id}"] = False
                        st.rerun()

        with btn_cols[1]:
            if st.button("✏️ Edit", key=f"cq_edit_{row_id}"):
                st.session_state[f"cq_editing_{row_id}"] = not st.session_state.get(f"cq_editing_{row_id}", False)
                st.rerun()

        with btn_cols[2]:
            if st.button("🔄 Regenerate", key=f"cq_regen_{row_id}"):
                ok = _api("post", f"/posts/{row_id}/regenerate", api_url)
                if ok:
                    st.toast("🔄 Regenerating post…")
                else:
                    st.toast("⚠️ Regenerate request sent (API may be offline)")

        with btn_cols[3]:
            if st.button("🗑️", key=f"cq_delete_{row_id}", help="Delete post"):
                ok = _api("delete", f"/posts/{row_id}", api_url)
                db.delete_content(row_id)
                st.rerun()

        # Approve options panel
        if showing_approve and status in ("draft",):
            st.markdown(
                '<div class="approve-options"><div class="approve-title">Choose how to publish:</div></div>',
                unsafe_allow_html=True,
            )
            opt1, opt2 = st.columns(2)
            with opt1:
                if st.button("📤 Post Now", key=f"cq_postnow_{row_id}", use_container_width=True):
                    if not st.session_state.get("linkedin_access_token"):
                        st.warning("⚠️ Connect LinkedIn to post directly. Use 'Save as Draft' to save for manual posting.")
                    else:
                        try:
                            r    = _requests.post(f"{api_url}/posts/{row_id}/publish", timeout=15)
                            data = r.json()
                            if data.get("ok"):
                                db.update_content_status(row_id, "posted")
                                st.session_state[f"cq_approving_{row_id}"] = False
                                li_id = data.get("linkedin_post_id", "")
                                st.toast(f"✅ Posted to LinkedIn!{' ID: ' + li_id if li_id else ''}")
                                st.rerun()
                            else:
                                st.toast(f"⚠️ {data.get('error', 'Publish failed')}")
                        except Exception as e:
                            st.toast(f"⚠️ Error: {e}")
            with opt2:
                if st.button("📝 Save as Draft", key=f"cq_savedraft_{row_id}", use_container_width=True):
                    _api("post", f"/posts/{row_id}/draft", api_url)
                    db.update_content_status(row_id, "draft_saved")
                    st.session_state[f"cq_approving_{row_id}"] = False
                    st.toast("📝 Saved to LinkedIn drafts")
                    st.rerun()

        # Inline edit form
        if st.session_state.get(f"cq_editing_{row_id}"):
            with st.form(key=f"cq_edit_form_{row_id}"):
                new_body = st.text_area("Edit post", value=body, height=200)
                char_warning = ""
                if len(new_body) > 3000:
                    char_warning = f"⚠️ {len(new_body)} chars — over LinkedIn 3000 char limit"
                elif len(new_body) > 2500:
                    char_warning = f"⚠️ {len(new_body)} chars — approaching limit"
                if char_warning:
                    st.warning(char_warning)
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


def render(api_url: str = "http://localhost:8000") -> None:
    drafts = db.get_content_queue("draft")
    draft_saved = db.get_content_queue("draft_saved")
    scheduled = db.get_content_queue("scheduled")
    posted = db.get_content_queue("posted")

    d_label = f"🟡 Drafts ({len(drafts)})" if drafts else "🟡 Drafts"
    s_label = f"🔵 Scheduled ({len(scheduled)})" if scheduled else "🔵 Scheduled"

    sub1, sub2, sub3, sub4 = st.tabs([d_label, "📝 Saved Drafts", s_label, "🟢 Posted"])

    with sub1:
        _render_cards(drafts, api_url)

    with sub2:
        _render_cards(draft_saved, api_url)

    with sub3:
        _render_cards(scheduled, api_url)

    with sub4:
        _render_cards(posted, api_url)
