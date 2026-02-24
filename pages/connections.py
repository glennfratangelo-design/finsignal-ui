"""
Connection Queue — manage pending, sent, accepted, and dismissed connection requests.
"""

import streamlit as st
import db

_CSS = """
<style>
.conn-card {
    background: #1E2130;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.conn-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 2px;
}
.conn-headline {
    font-size: 0.8rem;
    color: #9AA0B2;
    margin-bottom: 6px;
}
.conn-reason {
    font-size: 0.82rem;
    color: #CBD5E1;
    margin-bottom: 8px;
    line-height: 1.4;
}
.pill {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #fff;
    margin-right: 4px;
}
.pill-discover  { background: #0A66C2; }
.pill-sent      { background: #057642; }
.pill-accepted  { background: #065F46; }
.pill-dismissed { background: #374151; }
.pill-manual    { background: #92400E; color: #FDE68A; }
.auto-banner {
    background: #0F2942;
    border: 1px solid #0A66C2;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 0.83rem;
    color: #93C5FD;
}
.manual-banner {
    background: #1C1A0A;
    border: 1px solid #F5A623;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 0.83rem;
    color: #F5A623;
}
.empty-state {
    text-align: center;
    color: #6B7280;
    font-size: 0.88rem;
    padding: 36px 0;
}
.section-label {
    font-size: 0.85rem;
    font-weight: 700;
    color: #9AA0B2;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 10px;
    margin-top: 4px;
}
</style>
"""


def _source_pill(source: str) -> str:
    return f'<span class="pill pill-discover">{source or "discover"}</span>'


def _status_pill(status: str) -> str:
    if status == "sent":
        return '<span class="pill pill-sent">Sent</span>'
    if status == "accepted":
        return '<span class="pill pill-accepted">Accepted</span>'
    if status == "dismissed":
        return '<span class="pill pill-dismissed">Dismissed</span>'
    if status == "pending_manual":
        return '<span class="pill pill-manual">Manual</span>'
    return '<span class="pill" style="background:#374151;">Pending</span>'


def _fmt_date(dt_str: str) -> str:
    if not dt_str:
        return "—"
    return (dt_str or "")[:10]


def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
        "Connection Queue</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:16px;'>"
        "People waiting to connect with you.</div>",
        unsafe_allow_html=True,
    )

    # Load all connections
    all_conns = db.get_connections()
    pending   = [c for c in all_conns if c["status"] in ("pending", "pending_manual")]
    sent      = [c for c in all_conns if c["status"] == "sent"]
    accepted  = [c for c in all_conns if c["status"] == "accepted"]
    dismissed = [c for c in all_conns if c["status"] == "dismissed"]

    # Strategy for auto-send banner
    cfg = db.get_strategy()
    auto_send = cfg.get("connection_auto_send", False)

    # Filter chips
    filter_val = st.session_state.get("conn_filter", "Pending")
    counts = {
        "Pending":  len(pending),
        "Sent":     len(sent),
        "Accepted": len(accepted),
        "Dismissed": len(dismissed),
    }
    f1, f2, f3, f4, _ = st.columns([1, 1, 1, 1, 3])
    for col, label in zip([f1, f2, f3, f4], ["Pending", "Sent", "Accepted", "Dismissed"]):
        with col:
            cnt = counts[label]
            is_active = filter_val == label
            if st.button(
                f"{label} ({cnt})",
                key=f"conn_filter_{label}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.conn_filter = label
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    active_filter = st.session_state.get("conn_filter", "Pending")

    # ── PENDING ────────────────────────────────────────────────────────────────
    if active_filter == "Pending":
        if auto_send:
            st.markdown(
                "<div class='auto-banner'>🤖 Auto-send active — connections will be sent automatically "
                "within your configured send window.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='manual-banner'>⚠️ Manual mode — approve each connection before sending. "
                "Enable auto-send in Strategy → Connection Growth.</div>",
                unsafe_allow_html=True,
            )

        if not pending:
            st.markdown(
                "<div class='empty-state'>No pending connections. "
                "Go to Influencer Manager → Discover to find new people to connect with.</div>",
                unsafe_allow_html=True,
            )
        else:
            for c in pending:
                cid      = c["id"]
                name     = c.get("name") or "Unknown"
                handle   = c.get("linkedin_handle") or ""
                headline = c.get("headline") or ""
                reason   = c.get("reason") or ""
                source   = c.get("source") or "discover"
                url      = f"https://www.linkedin.com/in/{handle}/" if handle else "#"

                st.markdown(
                    f"<div class='conn-card'>"
                    f"<div class='conn-name'>{name} "
                    f"<a href='{url}' target='_blank' style='font-size:0.78rem;color:#0A66C2;"
                    f"text-decoration:none;font-weight:400;'>@{handle}</a></div>"
                    f"<div class='conn-headline'>{headline}</div>"
                    f"<div class='conn-reason'>{reason}</div>"
                    f"{_source_pill(source)}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                send_col, dismiss_col, _ = st.columns([1, 1, 4])
                with send_col:
                    if st.button(
                        "Send Connection",
                        key=f"conn_send_{cid}",
                        type="primary",
                        use_container_width=True,
                    ):
                        result = db.send_connection(cid)
                        st.toast(f"Connection sent to {name}")
                        st.rerun()
                with dismiss_col:
                    if st.button("Dismiss", key=f"conn_dismiss_{cid}", use_container_width=True):
                        db.dismiss_connection(cid)
                        st.rerun()

    # ── SENT ───────────────────────────────────────────────────────────────────
    elif active_filter == "Sent":
        if not sent:
            st.markdown("<div class='empty-state'>No connections sent yet.</div>", unsafe_allow_html=True)
        else:
            for c in sent:
                name   = c.get("name") or "Unknown"
                handle = c.get("linkedin_handle") or ""
                url    = f"https://www.linkedin.com/in/{handle}/" if handle else "#"
                sent_date = _fmt_date(c.get("sent_at"))
                st.markdown(
                    f"<div style='display:flex;align-items:center;padding:10px 0;"
                    f"border-bottom:1px solid #2D3748;gap:12px;'>"
                    f"<span style='flex:2;font-size:0.88rem;font-weight:700;color:#FAFAFA;'>{name}</span>"
                    f"<span style='flex:2;font-size:0.82rem;'>"
                    f"<a href='{url}' target='_blank' style='color:#0A66C2;text-decoration:none;'>"
                    f"@{handle}</a></span>"
                    f"<span style='flex:1;font-size:0.78rem;color:#6B7280;'>{sent_date}</span>"
                    f"<span style='flex:1;'>{_status_pill('sent')}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ── ACCEPTED ───────────────────────────────────────────────────────────────
    elif active_filter == "Accepted":
        if not accepted:
            st.markdown("<div class='empty-state'>No accepted connections yet.</div>", unsafe_allow_html=True)
        else:
            for c in accepted:
                name   = c.get("name") or "Unknown"
                handle = c.get("linkedin_handle") or ""
                url    = f"https://www.linkedin.com/in/{handle}/" if handle else "#"
                accepted_date = _fmt_date(c.get("accepted_at"))
                st.markdown(
                    f"<div style='display:flex;align-items:center;padding:10px 0;"
                    f"border-bottom:1px solid #2D3748;gap:12px;'>"
                    f"<span style='font-size:1rem;color:#22C55E;'>✓</span>"
                    f"<span style='flex:2;font-size:0.88rem;font-weight:700;color:#FAFAFA;'>{name}</span>"
                    f"<span style='flex:2;font-size:0.82rem;'>"
                    f"<a href='{url}' target='_blank' style='color:#0A66C2;text-decoration:none;'>"
                    f"@{handle}</a></span>"
                    f"<span style='flex:1;font-size:0.78rem;color:#6B7280;'>{accepted_date}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # ── DISMISSED ──────────────────────────────────────────────────────────────
    elif active_filter == "Dismissed":
        if not dismissed:
            st.markdown("<div class='empty-state'>No dismissed connections.</div>", unsafe_allow_html=True)
        else:
            for c in dismissed:
                name   = c.get("name") or "Unknown"
                handle = c.get("linkedin_handle") or ""
                dismissed_date = _fmt_date(c.get("dismissed_at"))
                st.markdown(
                    f"<div style='display:flex;align-items:center;padding:10px 0;"
                    f"border-bottom:1px solid #2D3748;gap:12px;color:#6B7280;'>"
                    f"<span style='flex:2;font-size:0.88rem;'>{name}</span>"
                    f"<span style='flex:2;font-size:0.82rem;'>@{handle}</span>"
                    f"<span style='flex:1;font-size:0.78rem;'>{dismissed_date}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
