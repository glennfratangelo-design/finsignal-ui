"""
Connections — shows sent connection requests from the last 30 days.
"""
import streamlit as st
import db

_CSS = """
<style>
.conn-row { display:flex; align-items:center; padding:10px 14px; border-bottom:1px solid #2D3748; gap:12px; }
.conn-row:hover { background:#1A1C2A; }
.empty-state { text-align:center; color:#6B7280; font-size:0.88rem; padding:48px 0; }
</style>
"""

def _fmt_date(dt_str):
    return (dt_str or "")[:10] if dt_str else "—"

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>Connections</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:16px;'>Connection requests sent in the last 30 days.</div>",
        unsafe_allow_html=True,
    )
    all_conns = db.get_connections()
    sent = [c for c in all_conns if c.get("status") == "sent"]
    total = len(sent)
    st.markdown(f"<div style='font-size:0.85rem;color:#9AA0B2;margin-bottom:14px;'>{total} connection{'s' if total != 1 else ''} sent</div>", unsafe_allow_html=True)
    if not sent:
        st.markdown("<div class='empty-state'>No connections sent yet. Add influencers from Discover to start building your network.</div>", unsafe_allow_html=True)
        return
    st.markdown(
        "<div style='display:flex;padding:6px 14px;border-bottom:2px solid #374151;font-size:0.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;gap:12px;'>"
        "<span style='flex:2;'>Name</span><span style='flex:2;'>Handle</span><span style='flex:1;'>Sent</span><span style='flex:1;'>Source</span></div>",
        unsafe_allow_html=True,
    )
    for c in sent:
        name = c.get("name") or "Unknown"
        handle = c.get("linkedin_handle") or ""
        url = f"https://www.linkedin.com/in/{handle}/" if handle else "#"
        sent_date = _fmt_date(c.get("sent_at"))
        source = c.get("source") or "discover"
        st.markdown(
            f"<div class='conn-row'>"
            f"<span style='flex:2;font-size:0.88rem;font-weight:700;color:#FAFAFA;'>{name}</span>"
            f"<span style='flex:2;font-size:0.82rem;'><a href='{url}' target='_blank' style='color:#0A66C2;text-decoration:none;'>@{handle}</a></span>"
            f"<span style='flex:1;font-size:0.78rem;color:#6B7280;'>{sent_date}</span>"
            f"<span style='flex:1;'><span style='display:inline-block;padding:2px 9px;border-radius:20px;font-size:0.68rem;font-weight:700;color:#fff;background:#0A66C2;'>{source}</span></span>"
            f"</div>",
            unsafe_allow_html=True,
        )
