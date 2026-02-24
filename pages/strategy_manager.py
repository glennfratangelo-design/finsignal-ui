"""
Strategy Manager page — Topic Intelligence, ICP, posting strategy, comment rules, quality gates.
"""

import streamlit as st
import db

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
<style>
/* ── Health cards ── */
.health-card {
    background: #1E2130;
    border-radius: 8px;
    padding: 16px 18px;
    border: 1px solid #2D3748;
    box-shadow: 0 1px 4px rgba(0,0,0,0.35);
    min-height: 90px;
}
.health-card.warn { border-left: 3px solid #F5A623; }
.health-card.ok   { border-left: 3px solid #22C55E; }
.health-label {
    font-size: 0.72rem;
    color: #9AA0B2;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}
.health-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FAFAFA;
    line-height: 1.1;
}
.health-sub {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 3px;
}
.flagged-item {
    background: #2D2010;
    border: 1px solid #F5A623;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 0.83rem;
    color: #F5A623;
    margin-bottom: 6px;
}
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 12px;
}

/* ── Topic cards ── */
.topic-card {
    background: #1E2130;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}
.topic-card.inactive { opacity: 0.5; }
.topic-tag {
    display: inline-block;
    background: #0A66C2;
    color: #fff;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.92rem;
    font-weight: 700;
    margin-bottom: 8px;
}
.topic-tag.inactive-tag { background: #374151; }
.topic-weight {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FAFAFA;
}
.topic-ctx {
    font-size: 0.78rem;
    color: #9AA0B2;
    margin-top: 6px;
    line-height: 1.5;
}

/* ── Chat UI ── */
.chat-outer {
    background: #141622;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 16px;
    height: 400px;
    overflow-y: auto;
    margin-bottom: 12px;
}
.chat-row-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
}
.chat-row-asst {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
}
.bubble-user {
    background: #0A66C2;
    color: #fff;
    padding: 10px 14px;
    border-radius: 12px 12px 2px 12px;
    max-width: 78%;
    font-size: 0.87rem;
    line-height: 1.5;
    white-space: pre-wrap;
}
.bubble-asst {
    background: #1E2130;
    color: #FAFAFA;
    padding: 10px 14px;
    border-radius: 12px 12px 12px 2px;
    max-width: 78%;
    font-size: 0.87rem;
    line-height: 1.5;
    border: 1px solid #2D3748;
    white-space: pre-wrap;
}

/* ── ICP profile card ── */
.icp-card {
    background: #1E2130;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}
.icp-label {
    font-size: 0.72rem;
    color: #9AA0B2;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
    margin-top: 12px;
}
.icp-value {
    font-size: 0.88rem;
    color: #FAFAFA;
    line-height: 1.6;
}
.pill {
    display: inline-block;
    background: #2D3748;
    color: #FAFAFA;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78rem;
    margin: 2px 4px 2px 0;
}
.empty-state {
    background: #1E2130;
    border: 1px dashed #4B5563;
    border-radius: 8px;
    padding: 32px;
    text-align: center;
    color: #6B7280;
    font-size: 0.88rem;
}

/* ── Feed rows ── */
.feed-list-header {
    font-size: 0.72rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 700;
    padding: 4px 0;
}
.cat-pill {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 20px;
    font-size: 0.67rem;
    font-weight: 700;
    color: #fff;
}
.add-form-panel {
    background: #161825;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 20px;
}

/* ── Feed discover cards ── */
.feed-disc-card {
    background: #1E2130;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.feed-disc-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 2px;
}
.feed-disc-url {
    font-size: 0.75rem;
    color: #0A66C2;
    word-break: break-all;
    margin-bottom: 6px;
}
.feed-disc-reason {
    font-size: 0.82rem;
    color: #CBD5E1;
    font-style: italic;
    margin-bottom: 8px;
    line-height: 1.4;
}
.feed-pattern-card {
    background: #1A2744;
    border: 1px solid #2563EB;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 0.85rem;
    color: #93C5FD;
    line-height: 1.5;
}
</style>
"""


# ── Session state helpers ─────────────────────────────────────────────────────

def _init_states() -> None:
    defaults = {
        # Voice Profile co-pilot state
        "sm_voice_chat_active": False,
        "sm_voice_conv_id":     None,
        "sm_voice_messages":    [],
        "sm_voice_draft":       None,
        # Topic co-pilot state
        "sm_topic_chat_active": False,
        "sm_topic_conv_id":     None,
        "sm_topic_messages":    [],
        "sm_topic_draft":       None,
        "sm_topic_edit_id":     None,
        # ICP co-pilot state
        "sm_icp_chat_active":   False,
        "sm_icp_conv_id":       None,
        "sm_icp_messages":      [],
        "sm_icp_draft":         None,
        # Feed sub-tab state
        "sm_feed_tab":           0,     # 0=Feeds, 1=Discover
        "sm_feed_adding":        False,
        "sm_feed_editing":       None,
        "sm_feed_delete_confirm": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Chat rendering ────────────────────────────────────────────────────────────

def _render_chat_messages(messages: list) -> None:
    """Render message bubbles in the chat container."""
    html = ["<div class='chat-outer' id='chat-scroll'>"]
    for msg in messages:
        text = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
        if msg["role"] == "user":
            html.append(f"<div class='chat-row-user'><div class='bubble-user'>{text}</div></div>")
        else:
            html.append(f"<div class='chat-row-asst'><div class='bubble-asst'>{text}</div></div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# ── Voice co-pilot UI ─────────────────────────────────────────────────────────

def _render_voice_copilot() -> None:
    st.markdown(
        "<div style='font-size:0.95rem;font-weight:700;color:#FAFAFA;margin-bottom:10px;'>"
        "Voice Setup Co-Pilot</div>",
        unsafe_allow_html=True,
    )

    messages = st.session_state.sm_voice_messages
    _render_chat_messages(messages)

    draft = st.session_state.sm_voice_draft
    if draft:
        st.success("Voice profile ready — review and confirm below.")
        tone_raw = draft.get("tone_descriptors", [])
        if isinstance(tone_raw, list):
            tone_pills = "".join(f"<span class='topic-tag'>{t}</span>&nbsp;" for t in tone_raw)
        else:
            tone_pills = f"<span class='topic-tag'>{tone_raw}</span>"
        st.markdown(
            f"<div class='icp-card' style='margin-bottom:12px;'>"
            f"<div class='icp-label'>Tone</div><div style='margin:4px 0;'>{tone_pills}</div>"
            f"<div class='icp-label'>Opens With</div>"
            f"<div class='icp-value'>{draft.get('opening_patterns', '')}</div>"
            f"<div class='icp-label'>Closes With</div>"
            f"<div class='icp-value'>{draft.get('closing_patterns', '')}</div>"
            f"<div class='icp-label'>Contrarian Level</div>"
            f"<div class='icp-value'>{draft.get('contrarian_level', 'medium')}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button("Confirm & Save Voice", key="sm_voice_confirm", type="primary"):
                conv_id = st.session_state.sm_voice_conv_id
                result  = db.confirm_voice_copilot(conv_id)
                if result.get("ok"):
                    st.toast("Voice profile saved — all posts will now sound like you.", icon="✅")
                    st.session_state.sm_voice_chat_active = False
                    st.session_state.sm_voice_messages    = []
                    st.session_state.sm_voice_draft       = None
                    st.session_state.sm_voice_conv_id     = None
                    st.rerun()
                else:
                    st.error(f"Save failed: {result.get('error', 'unknown error')}")
        with col2:
            if st.button("Start Over", key="sm_voice_restart"):
                st.session_state.sm_voice_messages = []
                st.session_state.sm_voice_draft    = None
                st.session_state.sm_voice_conv_id  = None
                st.rerun()
        with col3:
            if st.button("Cancel", key="sm_voice_cancel_draft"):
                st.session_state.sm_voice_chat_active = False
                st.session_state.sm_voice_messages    = []
                st.session_state.sm_voice_draft       = None
                st.session_state.sm_voice_conv_id     = None
                st.rerun()
        return

    input_col, btn_col = st.columns([5, 1])
    with input_col:
        user_input = st.text_input(
            "", key="sm_voice_input",
            placeholder="Share a post you wrote that felt most like you…",
            label_visibility="collapsed",
        )
    with btn_col:
        send = st.button("Send", key="sm_voice_send", use_container_width=True)

    cancel_col, _ = st.columns([1, 5])
    with cancel_col:
        if st.button("Cancel", key="sm_voice_cancel", use_container_width=True):
            st.session_state.sm_voice_chat_active = False
            st.session_state.sm_voice_messages    = []
            st.session_state.sm_voice_draft       = None
            st.session_state.sm_voice_conv_id     = None
            st.rerun()

    if send and user_input:
        with st.spinner("Thinking…"):
            conv_id = st.session_state.sm_voice_conv_id
            if conv_id is None:
                result = db.start_voice_copilot(user_input)
                if result.get("conversation_id"):
                    st.session_state.sm_voice_conv_id = result["conversation_id"]
            else:
                result = db.message_voice_copilot(conv_id, user_input)

        if "error" in result and not result.get("assistant_message"):
            st.error(f"Co-pilot error: {result['error']}")
            return

        msgs = st.session_state.sm_voice_messages
        msgs.append({"role": "user",      "content": user_input})
        msgs.append({"role": "assistant", "content": result.get("assistant_message", "")})
        st.session_state.sm_voice_messages = msgs

        if result.get("is_complete"):
            st.session_state.sm_voice_draft = result.get("voice_draft")

        st.rerun()


# ── Voice Profile section ─────────────────────────────────────────────────────

def _render_voice_section() -> None:
    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.markdown(
            "<div class='section-header'>Your Voice</div>", unsafe_allow_html=True
        )
        st.markdown(
            "<div style='font-size:0.82rem;color:#6B7280;margin-top:-8px;margin-bottom:12px;'>"
            "How you sound to the world. Every post and comment reflects this.</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.sm_voice_chat_active:
        _render_voice_copilot()
        _render_voice_learning()
        return

    vp = db.get_voice_profile()
    if not vp.get("exists") or vp.get("status") != "confirmed":
        st.markdown(
            "<div class='empty-state'>"
            "Your agents are using the baseline voice.<br>"
            "Define your authentic voice to make every post sound like you wrote it."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Start Voice Setup", key="sm_start_voice", type="primary"):
            st.session_state.sm_voice_chat_active = True
            st.session_state.sm_voice_messages    = []
            st.session_state.sm_voice_draft       = None
            st.session_state.sm_voice_conv_id     = None
            st.rerun()
        return

    # Voice profile confirmed — show profile card
    tone_raw = vp.get("tone_descriptors", [])
    if isinstance(tone_raw, list):
        tone_pills = "".join(f"<span class='topic-tag'>{t}</span>&nbsp;" for t in tone_raw)
    elif tone_raw:
        tone_pills = "".join(
            f"<span class='topic-tag'>{t.strip()}</span>&nbsp;"
            for t in str(tone_raw).split(",") if t.strip()
        )
    else:
        tone_pills = "<span class='icp-value'>Not set</span>"

    st.markdown(
        f"<div class='icp-card'>"
        f"<div class='icp-label'>Tone</div>"
        f"<div style='margin:6px 0;'>{tone_pills}</div>"
        f"<div class='icp-label'>Writing Patterns</div>"
        f"<div class='icp-value' style='margin-top:4px;'>"
        f"Opens with: {vp.get('opening_patterns', 'Not set')}<br>"
        f"Closes with: {vp.get('closing_patterns', 'Not set')}"
        f"</div>"
        f"<div class='icp-label'>Settings</div>"
        f"<div class='icp-value'>"
        f"Contrarian: {vp.get('contrarian_level', 'medium')} &nbsp;|&nbsp; "
        f"Humor: {vp.get('humor_level', 'dry')} &nbsp;|&nbsp; "
        f"Personal disclosure: {vp.get('personal_disclosure', 'occasional')}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    edit_col, reset_col, _ = st.columns([1, 1, 4])
    with edit_col:
        if st.button("Edit Voice", key="sm_edit_voice", type="primary"):
            tone_str = (
                ", ".join(tone_raw) if isinstance(tone_raw, list) else str(tone_raw)
            )
            edit_msg = (
                f"I want to refine my voice profile. My current tone is: {tone_str}. "
                f"I typically open posts like: {vp.get('opening_patterns', '')}. "
                "Please help me refine or update it."
            )
            st.session_state.sm_voice_chat_active    = True
            st.session_state.sm_voice_messages       = []
            st.session_state.sm_voice_draft          = None
            st.session_state.sm_voice_conv_id        = None
            st.session_state.sm_voice_edit_prefill   = edit_msg
            st.rerun()
    with reset_col:
        if st.button("Reset Voice", key="sm_reset_voice"):
            db.delete_voice_profile()
            st.toast("Voice profile reset", icon="🗑️")
            st.rerun()

    # Handle edit prefill
    if st.session_state.get("sm_voice_edit_prefill") and st.session_state.sm_voice_chat_active:
        prefill = st.session_state.pop("sm_voice_edit_prefill")
        with st.spinner("Loading voice profile for editing…"):
            result = db.start_voice_copilot(prefill)
        if result.get("conversation_id"):
            st.session_state.sm_voice_conv_id  = result["conversation_id"]
            st.session_state.sm_voice_messages = [
                {"role": "user",      "content": prefill},
                {"role": "assistant", "content": result.get("assistant_message", "")},
            ]
            if result.get("is_complete"):
                st.session_state.sm_voice_draft = result.get("voice_draft")
        st.rerun()

    _render_voice_learning()


def _render_voice_learning() -> None:
    """Render the 'What I've Learned' section from edit analysis."""
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header' style='font-size:0.9rem;'>What I've Learned</div>"
        "<div style='font-size:0.78rem;color:#6B7280;margin-top:-6px;margin-bottom:10px;'>"
        "Patterns detected from your edits — accept or reject each suggestion.</div>",
        unsafe_allow_html=True,
    )

    history = db.get_voice_history()
    pending = [h for h in history if h.get("source") == "edit_analysis" and h.get("accepted") == 0][:5]

    if not pending:
        st.markdown(
            "<div style='font-size:0.83rem;color:#6B7280;font-style:italic;'>"
            "No new patterns detected yet. Keep editing drafts to help me learn your voice.</div>",
            unsafe_allow_html=True,
        )
        return

    for item in pending:
        item_id   = item["id"]
        field     = item.get("field_changed", "").replace("_", " ").title()
        new_val   = item.get("new_value", "")
        created   = (item.get("created_at") or "")[:10]

        st.markdown(
            f"<div class='icp-card' style='padding:12px 16px;margin-bottom:8px;'>"
            f"<div style='font-size:0.75rem;color:#9AA0B2;text-transform:uppercase;"
            f"letter-spacing:0.06em;'>{field} &nbsp;·&nbsp; {created}</div>"
            f"<div style='font-size:0.85rem;color:#FAFAFA;margin-top:4px;'>{new_val}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        acc_col, rej_col, _ = st.columns([1, 1, 5])
        with acc_col:
            if st.button("✓ Accept", key=f"sm_vacc_{item_id}", use_container_width=True, type="primary"):
                db.accept_voice_change(item_id)
                st.toast("Change applied to voice profile", icon="✅")
                st.rerun()
        with rej_col:
            if st.button("✕ Reject", key=f"sm_vrej_{item_id}", use_container_width=True):
                db.reject_voice_change(item_id)
                st.rerun()


# ── Topic co-pilot UI ─────────────────────────────────────────────────────────

def _render_topic_copilot() -> None:
    """Inline topic co-pilot chat interface."""
    st.markdown(
        "<div style='font-size:0.95rem;font-weight:700;color:#FAFAFA;margin-bottom:10px;'>"
        "Topic Co-Pilot</div>",
        unsafe_allow_html=True,
    )

    messages = st.session_state.sm_topic_messages
    _render_chat_messages(messages)

    draft = st.session_state.sm_topic_draft
    if draft:
        st.success(f"**Draft ready: {draft.get('tag', '')}** — {draft.get('weight', 10)}% weight")
        st.markdown(
            f"<div style='font-size:0.82rem;color:#9AA0B2;background:#141622;"
            f"border:1px solid #2D3748;border-radius:6px;padding:12px;margin-bottom:12px;"
            f"white-space:pre-wrap;'>{draft.get('context', '')[:600]}...</div>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button("Confirm & Save Topic", key="sm_topic_confirm", type="primary"):
                conv_id = st.session_state.sm_topic_conv_id
                result  = db.confirm_topic_copilot(conv_id)
                if result.get("topic_id"):
                    st.toast("Topic saved!", icon="✅")
                    # Reset state
                    st.session_state.sm_topic_chat_active = False
                    st.session_state.sm_topic_messages    = []
                    st.session_state.sm_topic_draft       = None
                    st.session_state.sm_topic_conv_id     = None
                    st.rerun()
                else:
                    st.error(f"Save failed: {result.get('error', 'unknown error')}")
        with col2:
            if st.button("Start Over", key="sm_topic_restart"):
                st.session_state.sm_topic_messages = []
                st.session_state.sm_topic_draft    = None
                st.session_state.sm_topic_conv_id  = None
                st.rerun()
        with col3:
            if st.button("Cancel", key="sm_topic_cancel_draft"):
                st.session_state.sm_topic_chat_active = False
                st.session_state.sm_topic_messages    = []
                st.session_state.sm_topic_draft       = None
                st.session_state.sm_topic_conv_id     = None
                st.rerun()
        return

    # Input row
    input_col, btn_col = st.columns([5, 1])
    with input_col:
        user_input = st.text_input(
            "", key="sm_topic_input",
            placeholder="Describe the topic you want to cover…",
            label_visibility="collapsed",
        )
    with btn_col:
        send = st.button("Send", key="sm_topic_send", use_container_width=True)

    cancel_col, _ = st.columns([1, 5])
    with cancel_col:
        if st.button("Cancel", key="sm_topic_cancel", use_container_width=True):
            st.session_state.sm_topic_chat_active = False
            st.session_state.sm_topic_messages    = []
            st.session_state.sm_topic_draft       = None
            st.session_state.sm_topic_conv_id     = None
            st.rerun()

    if send and user_input:
        with st.spinner("Thinking…"):
            conv_id = st.session_state.sm_topic_conv_id
            if conv_id is None:
                result = db.start_topic_copilot(user_input)
                if result.get("conversation_id"):
                    st.session_state.sm_topic_conv_id = result["conversation_id"]
            else:
                result = db.message_topic_copilot(conv_id, user_input)

        if "error" in result and not result.get("assistant_message"):
            st.error(f"Co-pilot error: {result['error']}")
            return

        msgs = st.session_state.sm_topic_messages
        msgs.append({"role": "user",      "content": user_input})
        msgs.append({"role": "assistant", "content": result.get("assistant_message", "")})
        st.session_state.sm_topic_messages = msgs

        if result.get("is_complete"):
            st.session_state.sm_topic_draft = result.get("topic_draft")

        st.rerun()


# ── Topic Intelligence section ────────────────────────────────────────────────

def _render_topic_intelligence() -> None:
    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.markdown("<div class='section-header'>Topic Intelligence</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.82rem;color:#6B7280;margin-top:-8px;margin-bottom:12px;'>"
            "Define what you post about and why. Topics drive content generation.</div>",
            unsafe_allow_html=True,
        )
    with btn_col:
        rb_col, add_col = st.columns(2)
        with rb_col:
            if st.button("⚖️ Rebalance", key="sm_rebalance_topics", use_container_width=True):
                db.rebalance_topics()
                st.toast("Topics rebalanced to 100%", icon="✅")
                st.rerun()
        with add_col:
            if st.button("+ Add Topic", key="sm_add_topic", type="primary", use_container_width=True):
                st.session_state.sm_topic_chat_active = True
                st.session_state.sm_topic_messages    = []
                st.session_state.sm_topic_draft       = None
                st.session_state.sm_topic_conv_id     = None
                st.rerun()

    # Show co-pilot if active
    if st.session_state.sm_topic_chat_active:
        _render_topic_copilot()
        return

    topics = db.get_topics()
    if not topics:
        st.markdown(
            "<div class='empty-state'>No topics yet. Click <strong>+ Add Topic</strong> "
            "to define your first content topic with the co-pilot.</div>",
            unsafe_allow_html=True,
        )
        return

    # Render topic cards 2-per-row
    for i in range(0, len(topics), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(topics):
                break
            t = topics[i + j]
            tid     = t["id"]
            tag     = t["tag"]
            weight  = t["weight"]
            active  = bool(t["active"])
            context = t.get("context", "")
            short   = context[:120] + "…" if len(context) > 120 else context

            with col:
                active_class = "" if active else " inactive"
                tag_class    = "topic-tag" if active else "topic-tag inactive-tag"
                st.markdown(
                    f"<div class='topic-card{active_class}'>"
                    f"<span class='{tag_class}'>{tag}</span>"
                    f"<div class='topic-weight'>{weight}%</div>"
                    f"<div class='topic-ctx'>{short}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                act_label = "Deactivate" if active else "Activate"
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(act_label, key=f"sm_toggle_{tid}", use_container_width=True):
                        db.toggle_topic_active(tid)
                        st.rerun()
                with c2:
                    if st.button("Edit", key=f"sm_edit_{tid}", use_container_width=True):
                        # Pre-populate chat with existing context for editing
                        edit_msg = (
                            f"I want to update the topic '{tag}'. "
                            f"Current context: {context[:400]}. "
                            "Please help me refine or expand it."
                        )
                        st.session_state.sm_topic_chat_active = True
                        st.session_state.sm_topic_messages    = []
                        st.session_state.sm_topic_draft       = None
                        st.session_state.sm_topic_conv_id     = None
                        st.session_state.sm_topic_edit_prefill = edit_msg
                        st.rerun()
                with c3:
                    if st.button("Delete", key=f"sm_del_{tid}", use_container_width=True):
                        db.delete_topic(tid)
                        st.toast(f"Deleted topic '{tag}'", icon="🗑️")
                        st.rerun()

    # Check if we need to prefill the chat after an edit click
    if st.session_state.get("sm_topic_edit_prefill") and st.session_state.sm_topic_chat_active:
        prefill = st.session_state.pop("sm_topic_edit_prefill")
        with st.spinner("Loading topic for editing…"):
            result = db.start_topic_copilot(prefill)
        if result.get("conversation_id"):
            st.session_state.sm_topic_conv_id  = result["conversation_id"]
            st.session_state.sm_topic_messages = [
                {"role": "user",      "content": prefill},
                {"role": "assistant", "content": result.get("assistant_message", "")},
            ]
            if result.get("is_complete"):
                st.session_state.sm_topic_draft = result.get("topic_draft")
        st.rerun()

    # Weight total indicator
    total_w = sum(t["weight"] for t in topics if t["active"])
    color   = "#22C55E" if total_w == 100 else "#F5A623"
    st.markdown(
        f"<span style='font-size:0.8rem;color:{color};'>Active topic weight total: {total_w}%"
        f"{' ✓' if total_w == 100 else ' — click Rebalance to fix'}</span>",
        unsafe_allow_html=True,
    )


# ── ICP co-pilot UI ───────────────────────────────────────────────────────────

def _render_icp_copilot() -> None:
    """Inline ICP co-pilot chat interface."""
    st.markdown(
        "<div style='font-size:0.95rem;font-weight:700;color:#FAFAFA;margin-bottom:10px;'>"
        "ICP Co-Pilot</div>",
        unsafe_allow_html=True,
    )

    messages = st.session_state.sm_icp_messages
    _render_chat_messages(messages)

    draft = st.session_state.sm_icp_draft
    if draft:
        st.success("ICP draft ready — review and confirm below.")
        st.markdown(
            f"<div style='font-size:0.82rem;color:#9AA0B2;background:#141622;"
            f"border:1px solid #2D3748;border-radius:6px;padding:12px;margin-bottom:12px;'>"
            f"<strong>{draft.get('summary', '')}</strong></div>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button("Confirm & Save ICP", key="sm_icp_confirm", type="primary"):
                conv_id = st.session_state.sm_icp_conv_id
                result  = db.confirm_icp_copilot(conv_id)
                if result.get("ok"):
                    st.toast("ICP profile saved — content will now be optimized for this audience.", icon="✅")
                    st.session_state.sm_icp_chat_active = False
                    st.session_state.sm_icp_messages    = []
                    st.session_state.sm_icp_draft       = None
                    st.session_state.sm_icp_conv_id     = None
                    st.rerun()
                else:
                    st.error(f"Save failed: {result.get('error', 'unknown error')}")
        with col2:
            if st.button("Start Over", key="sm_icp_restart"):
                st.session_state.sm_icp_messages = []
                st.session_state.sm_icp_draft    = None
                st.session_state.sm_icp_conv_id  = None
                st.rerun()
        with col3:
            if st.button("Cancel", key="sm_icp_cancel_draft"):
                st.session_state.sm_icp_chat_active = False
                st.session_state.sm_icp_messages    = []
                st.session_state.sm_icp_draft       = None
                st.session_state.sm_icp_conv_id     = None
                st.rerun()
        return

    input_col, btn_col = st.columns([5, 1])
    with input_col:
        user_input = st.text_input(
            "", key="sm_icp_input",
            placeholder="Tell me about the audience you're writing for…",
            label_visibility="collapsed",
        )
    with btn_col:
        send = st.button("Send", key="sm_icp_send", use_container_width=True)

    cancel_col, _ = st.columns([1, 5])
    with cancel_col:
        if st.button("Cancel", key="sm_icp_cancel", use_container_width=True):
            st.session_state.sm_icp_chat_active = False
            st.session_state.sm_icp_messages    = []
            st.session_state.sm_icp_draft       = None
            st.session_state.sm_icp_conv_id     = None
            st.rerun()

    if send and user_input:
        with st.spinner("Thinking…"):
            conv_id = st.session_state.sm_icp_conv_id
            if conv_id is None:
                result = db.start_icp_copilot(user_input)
                if result.get("conversation_id"):
                    st.session_state.sm_icp_conv_id = result["conversation_id"]
            else:
                result = db.message_icp_copilot(conv_id, user_input)

        if "error" in result and not result.get("assistant_message"):
            st.error(f"Co-pilot error: {result['error']}")
            return

        msgs = st.session_state.sm_icp_messages
        msgs.append({"role": "user",      "content": user_input})
        msgs.append({"role": "assistant", "content": result.get("assistant_message", "")})
        st.session_state.sm_icp_messages = msgs

        if result.get("is_complete"):
            st.session_state.sm_icp_draft = result.get("icp_draft")

        st.rerun()


# ── ICP section ───────────────────────────────────────────────────────────────

def _render_icp_section() -> None:
    header_col, btn_col = st.columns([3, 1])
    with header_col:
        st.markdown(
            "<div class='section-header'>Ideal Customer Profile</div>", unsafe_allow_html=True
        )
        st.markdown(
            "<div style='font-size:0.82rem;color:#6B7280;margin-top:-8px;margin-bottom:12px;'>"
            "Who are you writing for? Every post is optimized for this person.</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.sm_icp_chat_active:
        _render_icp_copilot()
        return

    icp = db.get_icp()
    if not icp.get("exists"):
        st.markdown(
            "<div class='empty-state'>"
            "No ICP defined yet.<br>"
            "Define your target audience to optimize every post for the right person."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Define your ICP", key="sm_define_icp", type="primary"):
            st.session_state.sm_icp_chat_active = True
            st.session_state.sm_icp_messages    = []
            st.session_state.sm_icp_draft       = None
            st.session_state.sm_icp_conv_id     = None
            st.rerun()
        return

    # ICP is defined — show profile card
    def _pills(items) -> str:
        if isinstance(items, list):
            return "".join(f"<span class='pill'>{i}</span>" for i in items)
        return f"<span class='icp-value'>{items}</span>"

    titles     = icp.get("target_titles", [])
    industries = icp.get("target_industries", [])
    geos       = icp.get("geographies", [])
    pains      = icp.get("pain_points", [])

    st.markdown(
        f"<div class='icp-card'>"
        f"<div class='icp-label'>Summary</div>"
        f"<div class='icp-value'>{icp.get('summary', '')}</div>"
        f"<div class='icp-label'>Target Titles</div>"
        f"<div>{_pills(titles)}</div>"
        f"<div class='icp-label'>Industries</div>"
        f"<div>{_pills(industries)}</div>"
        f"<div class='icp-label'>Geographies</div>"
        f"<div>{_pills(geos)}</div>"
        f"<div class='icp-label'>Pain Points</div>"
        f"<div class='icp-value'><ul style='margin:4px 0 0 16px;padding:0;'>"
        + "".join(f"<li>{p}</li>" for p in (pains if isinstance(pains, list) else [pains]))
        + "</ul></div>"
        f"<div class='icp-label'>Vocabulary</div>"
        f"<div class='icp-value'>{icp.get('vocabulary', '')}</div>"
        f"<div class='icp-label'>Positioning</div>"
        f"<div class='icp-value'>{icp.get('positioning', '')}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    edit_col, reset_col, _ = st.columns([1, 1, 4])
    with edit_col:
        if st.button("Edit ICP", key="sm_edit_icp", type="primary"):
            summary = icp.get("summary", "")
            edit_msg = (
                f"I want to update my ICP. Current summary: {summary[:300]}. "
                "Please help me refine it."
            )
            st.session_state.sm_icp_chat_active   = True
            st.session_state.sm_icp_messages      = []
            st.session_state.sm_icp_draft         = None
            st.session_state.sm_icp_conv_id       = None
            st.session_state.sm_icp_edit_prefill  = edit_msg
            st.rerun()
    with reset_col:
        if st.button("Reset ICP", key="sm_reset_icp"):
            db.delete_icp()
            st.toast("ICP profile reset", icon="🗑️")
            st.rerun()

    # Handle edit prefill
    if st.session_state.get("sm_icp_edit_prefill") and st.session_state.sm_icp_chat_active:
        prefill = st.session_state.pop("sm_icp_edit_prefill")
        with st.spinner("Loading ICP for editing…"):
            result = db.start_icp_copilot(prefill)
        if result.get("conversation_id"):
            st.session_state.sm_icp_conv_id  = result["conversation_id"]
            st.session_state.sm_icp_messages = [
                {"role": "user",      "content": prefill},
                {"role": "assistant", "content": result.get("assistant_message", "")},
            ]
            if result.get("is_complete"):
                st.session_state.sm_icp_draft = result.get("icp_draft")
        st.rerun()


# ── Feed section helpers ──────────────────────────────────────────────────────

import re as _re

_FEED_CATEGORIES = [
    "AML", "KYC", "Fraud", "Sanctions", "RegTech",
    "Regulatory", "Compliance", "Financial Crime", "Payments", "Other",
]

_FEED_CAT_COLORS = {
    "AML":             "#0A66C2",
    "KYC":             "#057642",
    "Fraud":           "#CC1016",
    "Sanctions":       "#E85D04",
    "RegTech":         "#7B2D8B",
    "Regulatory":      "#0891B2",
    "Compliance":      "#6366F1",
    "Financial Crime": "#DC2626",
    "Payments":        "#0284C7",
    "Other":           "#6B7280",
}


def _feed_cat_pill(category: str) -> str:
    color = _FEED_CAT_COLORS.get(category, "#555")
    return f'<span class="cat-pill" style="background:{color};">{category or "Other"}</span>'


def _feed_truncate_url(url: str, n: int = 45) -> str:
    return url[:n] + "…" if len(url) > n else url


def _feed_valid_url(url: str) -> bool:
    return bool(_re.match(r"https?://[^\s]+", url.strip()))


def _render_feed_form_sm(key_prefix: str, defaults: dict, on_save, on_cancel) -> None:
    st.markdown('<div class="add-form-panel">', unsafe_allow_html=True)
    with st.form(key=f"sm_feed_form_{key_prefix}"):
        fc1, fc2 = st.columns(2)
        with fc1:
            new_name = st.text_input("Feed Name *", value=defaults.get("name", ""))
            new_url  = st.text_input(
                "Feed URL *",
                value=defaults.get("url", ""),
                placeholder="https://example.com/feed/",
            )
            new_type = st.selectbox(
                "Feed Type",
                ["rss", "atom", "blog", "json"],
                index=["rss", "atom", "blog", "json"].index(defaults.get("feed_type", "rss")),
            )
        with fc2:
            new_category = st.selectbox(
                "Category",
                _FEED_CATEGORIES,
                index=_FEED_CATEGORIES.index(defaults.get("category", "Other"))
                if defaults.get("category") in _FEED_CATEGORIES
                else 0,
            )
            new_priority = st.radio(
                "Priority",
                ["standard", "priority"],
                index=0 if defaults.get("priority", "standard") == "standard" else 1,
                horizontal=True,
                format_func=lambda x: "⭐ Priority" if x == "priority" else "Standard",
            )
            new_active = st.checkbox(
                "Active (fetched by agent)", value=bool(defaults.get("active", True))
            )
        sc, cc = st.columns(2)
        with sc:
            if st.form_submit_button("Save Feed", use_container_width=True):
                if not new_name.strip():
                    st.error("Feed name is required.")
                elif not _feed_valid_url(new_url):
                    st.error("Enter a valid URL starting with http:// or https://")
                else:
                    on_save({
                        "name":      new_name.strip(),
                        "url":       new_url.strip(),
                        "feed_type": new_type,
                        "priority":  new_priority,
                        "category":  new_category,
                        "active":    new_active,
                    })
                    st.rerun()
        with cc:
            if st.form_submit_button("Cancel", use_container_width=True):
                on_cancel()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_feeds_tab() -> None:
    """Feeds sub-tab: list view with add/edit/delete."""
    # Header row
    hdr_l, hdr_r = st.columns([4, 1])
    with hdr_l:
        all_f = db.get_feeds()
        priority_f = [f for f in all_f if f.get("priority") == "priority"]
        active_f   = [f for f in all_f if f.get("active")]
        st.markdown(
            f"<div style='font-size:0.78rem;color:#6B7280;margin-bottom:12px;'>"
            f"{len(all_f)} feeds &nbsp;·&nbsp; {len(priority_f)} priority &nbsp;·&nbsp; {len(active_f)} active</div>",
            unsafe_allow_html=True,
        )
    with hdr_r:
        showing = st.session_state.sm_feed_adding
        if st.button(
            "✕ Cancel" if showing else "➕ Add Feed",
            key="sm_feed_add_toggle",
            type="secondary" if showing else "primary",
            use_container_width=True,
        ):
            st.session_state.sm_feed_adding = not showing
            st.session_state.sm_feed_editing = None
            st.rerun()

    # Add form
    if st.session_state.sm_feed_adding:
        _render_feed_form_sm(
            key_prefix="new",
            defaults={"feed_type": "rss", "priority": "standard", "category": "AML", "active": True},
            on_save=lambda d: (
                db.save_feed(d["name"], d["url"], d["feed_type"], d["priority"], d["category"], int(d["active"])),
                st.session_state.update({"sm_feed_adding": False}),
            ),
            on_cancel=lambda: st.session_state.update({"sm_feed_adding": False}),
        )

    # Load feeds — priority first
    all_feeds  = db.get_feeds()
    pri_feeds  = [f for f in all_feeds if f.get("priority") == "priority"]
    std_feeds  = [f for f in all_feeds if f.get("priority") != "priority"]
    sorted_feeds = pri_feeds + std_feeds

    if not sorted_feeds:
        st.markdown(
            "<div class='empty-state'>"
            "No feeds added yet. Use the <strong>Discover</strong> tab to find relevant RSS feeds, "
            "or add one manually above.<br/><br/>"
            "<span style='font-size:0.78rem;color:#4B5563;'>"
            "New users start with no feeds. Use the Discover tab to populate your feed list "
            "based on your topics and industry.</span></div>",
            unsafe_allow_html=True,
        )
        return

    # List header
    lh1, lh2, lh3, _, _, _, _ = st.columns([3.5, 1.2, 1.2, 0.6, 0.6, 0.6, 0.6])
    for col, label in [(lh1, "Feed"), (lh2, "Category"), (lh3, "Last Fetched")]:
        col.markdown(
            f"<div class='feed-list-header'>{label}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    for feed in sorted_feeds:
        row_id    = feed["id"]
        name      = feed["name"]
        url       = feed.get("url") or ""
        category  = feed.get("category") or "Other"
        priority  = feed.get("priority") or "standard"
        feed_type = feed.get("feed_type") or "rss"
        active    = int(feed.get("active", 1))
        last_str  = (feed.get("last_fetched") or "")[:10] or "Never"

        # Delete confirmation
        if st.session_state.sm_feed_delete_confirm == row_id:
            st.warning(f"Remove **{name}** from your research feeds?")
            dc, cc2, _ = st.columns([1, 1, 4])
            with dc:
                if st.button("Confirm Remove", key=f"sm_feed_delconf_{row_id}", type="primary"):
                    db.delete_feed(row_id)
                    st.session_state.sm_feed_delete_confirm = None
                    st.toast(f"Removed {name}", icon="🗑️")
                    st.rerun()
            with cc2:
                if st.button("Cancel", key=f"sm_feed_delcancel_{row_id}"):
                    st.session_state.sm_feed_delete_confirm = None
                    st.rerun()
            continue

        c_info, c_cat, c_last, c_star, c_tog, c_edit, c_del = st.columns([3.5, 1.2, 1.2, 0.6, 0.6, 0.6, 0.6])
        with c_info:
            st.markdown(
                f"<div style='padding:6px 0;'>"
                f"<span style='font-size:0.88rem;font-weight:700;color:#FAFAFA;'>{name}</span>&nbsp;"
                f"<a href='{url}' target='_blank' style='font-size:0.72rem;color:#0A66C2;'>"
                f"{_feed_truncate_url(url, 40)}</a></div>",
                unsafe_allow_html=True,
            )
        with c_cat:
            st.markdown(
                f"<div style='padding:8px 0;'>{_feed_cat_pill(category)}</div>",
                unsafe_allow_html=True,
            )
        with c_last:
            st.markdown(
                f"<div style='padding:6px 0;font-size:0.72rem;color:#6B7280;'>{last_str}</div>",
                unsafe_allow_html=True,
            )
        with c_star:
            star = "⭐" if priority == "priority" else "☆"
            if st.button(star, key=f"sm_feed_star_{row_id}", help="Toggle priority", use_container_width=True):
                new_p = "standard" if priority == "priority" else "priority"
                db.update_feed(row_id, name, url, feed_type, new_p, category, active)
                st.rerun()
        with c_tog:
            if st.button(
                "⏸" if active else "▶",
                key=f"sm_feed_toggle_{row_id}",
                help="Pause/Resume",
                use_container_width=True,
            ):
                db.toggle_feed_active(row_id, 0 if active else 1)
                st.rerun()
        with c_edit:
            if st.button("✏️", key=f"sm_feed_edit_{row_id}", help="Edit", use_container_width=True):
                current = st.session_state.sm_feed_editing
                st.session_state.sm_feed_editing = None if current == row_id else row_id
                st.session_state.sm_feed_adding  = False
                st.rerun()
        with c_del:
            if st.button("🗑️", key=f"sm_feed_del_{row_id}", help="Delete", use_container_width=True):
                st.session_state.sm_feed_delete_confirm = row_id
                st.rerun()

    # Inline edit form
    editing_id = st.session_state.sm_feed_editing
    if editing_id:
        editing_feed = next((f for f in sorted_feeds if f["id"] == editing_id), None)
        if editing_feed:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _render_feed_form_sm(
                key_prefix=f"edit_{editing_id}",
                defaults={
                    "name":      editing_feed["name"],
                    "url":       editing_feed.get("url", ""),
                    "feed_type": editing_feed.get("feed_type", "rss"),
                    "priority":  editing_feed.get("priority", "standard"),
                    "category":  editing_feed.get("category", "Other"),
                    "active":    bool(int(editing_feed.get("active", 1))),
                },
                on_save=lambda d: (
                    db.update_feed(
                        editing_id, d["name"], d["url"], d["feed_type"],
                        d["priority"], d["category"], int(d["active"])
                    ),
                    st.session_state.update({"sm_feed_editing": None}),
                ),
                on_cancel=lambda: st.session_state.update({"sm_feed_editing": None}),
            )


def _render_feed_discover_tab() -> None:
    """Discover sub-tab: AI feed suggestions."""
    st.markdown(
        "<div style='font-size:0.82rem;color:#6B7280;margin-bottom:14px;'>"
        "AI-powered RSS feed recommendations based on your topics and industry.</div>",
        unsafe_allow_html=True,
    )

    # Load suggestions
    suggestions = db.get_feed_suggestions()

    if not suggestions:
        st.markdown(
            "<div class='empty-state'>Generating suggestions…</div>",
            unsafe_allow_html=True,
        )
        with st.spinner("Calling Claude…"):
            db.generate_feed_suggestions()
        st.rerun()
        return

    for s in suggestions:
        sid      = s["id"]
        name     = s.get("name") or "Unknown Feed"
        url      = s.get("url") or ""
        category = s.get("category") or "Other"
        reason   = s.get("reason") or ""

        st.markdown(
            f"<div class='feed-disc-card'>"
            f"<div class='feed-disc-name'>{name}</div>"
            f"<div class='feed-disc-url'>"
            f"<a href='{url}' target='_blank' style='color:#0A66C2;text-decoration:none;'>{url}</a>"
            f"</div>"
            f"{_feed_cat_pill(category)}"
            f"<div class='feed-disc-reason' style='margin-top:8px;'>{reason}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        btn_l, btn_r, _ = st.columns([1, 1, 4])
        with btn_l:
            if st.button(
                "➕ Add Feed",
                key=f"sm_fdacc_{sid}",
                type="primary",
                use_container_width=True,
                help="Adds to your feeds list",
            ):
                db.accept_feed_suggestion(sid)
                st.toast(f"Added {name} to feeds")
                st.rerun()
        with btn_r:
            if st.button(
                "Not relevant",
                key=f"sm_fddis_{sid}",
                use_container_width=True,
            ):
                db.dismiss_feed_suggestion(sid)
                st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Suggestions", key="sm_fd_refresh"):
        with st.spinner("Generating new suggestions…"):
            db.generate_feed_suggestions()
        st.toast("New suggestions generating…")
        st.rerun()

    st.markdown(
        "<div style='font-size:0.75rem;color:#4B5563;margin-top:12px;'>"
        "New users start with no feeds. Use this tab to populate your feed list "
        "based on your topics and industry.</div>",
        unsafe_allow_html=True,
    )


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    _init_states()

    st.markdown(
        "<div style='font-size:1.3rem;font-weight:800;color:#FAFAFA;margin-bottom:4px;'>"
        "Strategy Manager</div>"
        "<div style='font-size:0.83rem;color:#6B7280;margin-bottom:20px;'>"
        "Configure topics, ICP, posting limits, content mix, comment rules, and quality gates.</div>",
        unsafe_allow_html=True,
    )

    # ── Section 1: Voice Profile ────────────────────────────────────────────────
    _render_voice_section()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 2: Topic Intelligence ──────────────────────────────────────────
    _render_topic_intelligence()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 3: ICP ─────────────────────────────────────────────────────────
    _render_icp_section()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    cfg    = db.get_strategy()
    health = db.get_strategy_health()

    # ── Section 4: Strategy Health ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>Strategy Health</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    comments_today = health["comments_today"]
    max_comments   = health["max_comments_day"]
    posts_week     = health["posts_this_week"]
    max_posts      = health["max_posts_week"]
    archived       = health["archived_this_week"]

    with c1:
        warn = comments_today >= max_comments
        st.markdown(
            f"""<div class='health-card {"warn" if warn else "ok"}'>
                <div class='health-label'>Comments Today</div>
                <div class='health-value'>{comments_today}/{max_comments}</div>
                <div class='health-sub'>{"⚠ Limit reached" if warn else "Within limit"}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        warn = posts_week >= max_posts
        st.markdown(
            f"""<div class='health-card {"warn" if warn else "ok"}'>
                <div class='health-label'>Posts This Week</div>
                <div class='health-value'>{posts_week}/{max_posts}</div>
                <div class='health-sub'>{"⚠ Limit reached" if warn else "Within limit"}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        pct = round((posts_week / max_posts) * 100) if max_posts else 0
        st.markdown(
            f"""<div class='health-card ok'>
                <div class='health-label'>Weekly Pacing</div>
                <div class='health-value'>{pct}%</div>
                <div class='health-sub'>of weekly target used</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        warn = archived > 0
        st.markdown(
            f"""<div class='health-card {"warn" if warn else "ok"}'>
                <div class='health-label'>Archived (Quality)</div>
                <div class='health-value'>{archived}</div>
                <div class='health-sub'>posts failed quality gate this week</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Topic distribution
    topic_dist     = health.get("topic_distribution", {})
    target_weights = health.get("target_weights", {})
    if topic_dist:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-header' style='font-size:0.88rem;'>Topic Distribution This Week</div>",
            unsafe_allow_html=True,
        )
        bar_cols = st.columns(len(topic_dist))
        for col, (topic, count) in zip(bar_cols, topic_dist.items()):
            target       = target_weights.get(topic, 0)
            target_posts = round((target / 100) * max_posts) if target else 0
            col.metric(label=topic, value=count, delta=f"target {target_posts}")

    flagged = health.get("flagged_items", [])
    if flagged:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        for item in flagged:
            st.markdown(f"<div class='flagged-item'>{item}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 4: Posting Strategy ────────────────────────────────────────────
    st.markdown("<div class='section-header'>Posting Strategy</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        new_max_posts_day = st.number_input(
            "Max posts per day",
            min_value=1, max_value=10,
            value=int(cfg.get("max_posts_per_day", 2)),
            key="strat_max_posts_day",
        )
        new_max_posts_week = st.number_input(
            "Max posts per week",
            min_value=1, max_value=30,
            value=int(cfg.get("max_posts_per_week", 8)),
            key="strat_max_posts_week",
        )

    with col_r:
        times_raw = cfg.get("best_posting_times", ["08:00", "12:00", "17:00"])
        times_str = st.text_input(
            "Best posting times (comma-separated, 24h)",
            value=", ".join(times_raw),
            key="strat_post_times",
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("**Topic Allocation (must total 100%)**")

    weights = dict(cfg.get("topic_weights", {"AML": 30, "KYC": 15, "Fraud": 20, "AI/Agentic": 25, "Sanctions": 10}))
    new_weights = {}
    wc = st.columns(len(weights))
    for i, (topic, pct) in enumerate(weights.items()):
        with wc[i]:
            new_weights[topic] = st.slider(topic, 0, 100, int(pct), key=f"strat_weight_{topic}")

    total_pct = sum(new_weights.values())
    pct_color = "#22C55E" if total_pct == 100 else "#F5A623"
    st.markdown(
        f"<span style='font-size:0.83rem;color:{pct_color};'>Total: {total_pct}%</span>",
        unsafe_allow_html=True,
    )
    if total_pct != 100 and st.button("Rebalance to 100%", key="strat_rebalance"):
        if total_pct > 0:
            scale = 100 / total_pct
            new_weights = {k: max(1, round(v * scale)) for k, v in new_weights.items()}
            diff = 100 - sum(new_weights.values())
            if diff != 0:
                biggest = max(new_weights, key=new_weights.get)
                new_weights[biggest] += diff
            st.rerun()

    if st.button("Save Posting Strategy", key="strat_save_posting", type="primary"):
        times_list = [t.strip() for t in times_str.split(",") if t.strip()]
        db.update_strategy({
            "max_posts_per_day":  new_max_posts_day,
            "max_posts_per_week": new_max_posts_week,
            "best_posting_times": times_list,
            "topic_weights":      new_weights,
        })
        st.toast("Posting strategy saved", icon="✅")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 5: Comment Co-Pilot ────────────────────────────────────────────
    st.markdown("<div class='section-header'>Comment Co-Pilot</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        new_max_comments_day = st.number_input(
            "Max comments per day",
            min_value=1, max_value=20,
            value=int(cfg.get("max_comments_per_day", 5)),
            key="strat_max_comments_day",
        )
        new_max_per_inf = st.number_input(
            "Max comments per influencer per week",
            min_value=1, max_value=10,
            value=int(cfg.get("max_comments_per_influencer_per_week", 2)),
            key="strat_max_per_inf",
        )
        new_cooldown = st.number_input(
            "Cooldown hours between comments",
            min_value=1, max_value=168,
            value=int(cfg.get("comment_cooldown_hours", 48)),
            key="strat_cooldown",
        )

    with col_r:
        tone_rules = cfg.get("comment_tone_rules", [])
        tone_raw   = st.text_area(
            "Tone rules (one per line)",
            value="\n".join(tone_rules),
            height=130,
            key="strat_tone_rules",
        )
        avoided_raw = st.text_area(
            "Avoided intent keywords (one per line)",
            value="\n".join(cfg.get("avoided_intent_keywords", [])),
            height=100,
            key="strat_avoided",
        )

    never_raw = st.text_input(
        "Never-comment accounts (comma-separated handles)",
        value=", ".join(cfg.get("never_comment_accounts", [])),
        key="strat_never_accounts",
    )

    if st.button("Save Comment Co-Pilot", key="strat_save_comments", type="primary"):
        db.update_strategy({
            "max_comments_per_day":                 new_max_comments_day,
            "max_comments_per_influencer_per_week": new_max_per_inf,
            "comment_cooldown_hours":               new_cooldown,
            "comment_tone_rules":                   [r.strip() for r in tone_raw.splitlines() if r.strip()],
            "avoided_intent_keywords":              [k.strip() for k in avoided_raw.splitlines() if k.strip()],
            "never_comment_accounts":               [a.strip() for a in never_raw.split(",") if a.strip()],
        })
        st.toast("Comment settings saved", icon="✅")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 6: Quality Gate ─────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Quality Gate</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:0.83rem;color:#9AA0B2;margin-bottom:12px;'>"
        "Posts scoring below the minimum threshold will be regenerated once. "
        "If still below, they're archived and excluded from the content queue.</div>",
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([2, 1])
    with col_l:
        new_min_score = st.slider(
            "Minimum post quality score (1–10)",
            min_value=1, max_value=10,
            value=int(cfg.get("min_post_quality_score", 7)),
            key="strat_min_score",
        )
    with col_r:
        warn = archived > 0
        st.markdown(
            f"""<div class='health-card {"warn" if warn else "ok"}' style='margin-top:6px;'>
                <div class='health-label'>Archived This Week</div>
                <div class='health-value'>{archived}</div>
                <div class='health-sub'>posts rejected</div>
            </div>""",
            unsafe_allow_html=True,
        )

    if st.button("Save Quality Gate", key="strat_save_quality", type="primary"):
        db.update_strategy({"min_post_quality_score": new_min_score})
        st.toast("Quality gate saved", icon="✅")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 7: Connection Growth ───────────────────────────────────────────
    st.markdown("<div class='section-header'>Connection Growth</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.83rem;color:#9AA0B2;margin-bottom:16px;'>"
        "Configure how FinSignal sends LinkedIn connection requests on your behalf.</div>",
        unsafe_allow_html=True,
    )

    conn_auto = bool(cfg.get("connection_auto_send", False))
    new_auto  = st.toggle(
        "Automatically send connection requests",
        value=conn_auto,
        key="strat_conn_auto",
    )

    if new_auto:
        st.markdown(
            "<div style='background:#2D1A05;border:1px solid #F5A623;border-radius:6px;"
            "padding:10px 14px;font-size:0.82rem;color:#F5A623;margin-bottom:12px;'>"
            "⚠️ LinkedIn may flag automated connection patterns. FinSignal uses randomized timing "
            "and daily limits to minimize risk. <strong>You are responsible for compliance with "
            "LinkedIn's terms of service.</strong></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("**Connection Pace**", unsafe_allow_html=False)
    current_pace = cfg.get("connection_pace", "moderate")
    pace_options = ["slow", "moderate", "active"]
    pace_labels  = ["Slow (1-2/day)", "Moderate (3-5/day)", "Active (6-8/day)"]
    pace_idx     = pace_options.index(current_pace) if current_pace in pace_options else 1

    p1, p2, p3, _ = st.columns([1, 1, 1, 3])
    new_pace = current_pace
    for col, key, label in zip([p1, p2, p3], pace_options, pace_labels):
        with col:
            is_sel = current_pace == key
            if st.button(
                label,
                key=f"strat_pace_{key}",
                type="primary" if is_sel else "secondary",
                use_container_width=True,
            ):
                new_pace = key
    if new_pace == "active" and current_pace != "active":
        st.markdown(
            "<div style='background:#2D1A05;border:1px solid #F5A623;border-radius:6px;"
            "padding:8px 12px;font-size:0.8rem;color:#F5A623;margin-top:6px;'>"
            "Higher volumes increase detection risk. Consider staying at Moderate.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    pause_weekends = bool(cfg.get("connection_pause_weekends", True))
    new_pause_weekends = st.toggle(
        "Pause on weekends",
        value=pause_weekends,
        key="strat_conn_pause_weekends",
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("Save Connection Settings", key="strat_save_conn", type="primary"):
        db.update_strategy({
            "connection_auto_send":      new_auto,
            "connection_pace":           new_pace,
            "connection_pause_weekends": new_pause_weekends,
        })
        st.toast("Connection settings saved", icon="✅")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2D3748;'/>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Section 8: Research Agent Data Feeds ───────────────────────────────────
    st.markdown("<div class='section-header'>Research Agent Data Feeds</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.83rem;color:#9AA0B2;margin-bottom:16px;'>"
        "RSS and blog sources monitored by the research agent.</div>",
        unsafe_allow_html=True,
    )

    # Sub-tab navigation
    ftab_l, ftab_r, _ = st.columns([1, 1, 4])
    with ftab_l:
        if st.button(
            "📋  Feeds",
            key="sm_ftab_feeds",
            type="primary" if st.session_state.sm_feed_tab == 0 else "secondary",
            use_container_width=True,
        ):
            st.session_state.sm_feed_tab = 0
            st.rerun()
    with ftab_r:
        if st.button(
            "✨  Discover",
            key="sm_ftab_discover",
            type="primary" if st.session_state.sm_feed_tab == 1 else "secondary",
            use_container_width=True,
        ):
            st.session_state.sm_feed_tab = 1
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.session_state.sm_feed_tab == 0:
        _render_feeds_tab()
    else:
        _render_feed_discover_tab()
