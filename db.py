"""
FinSignal UI — Data layer.
All reads and writes go through the FastAPI backend API.
Railway volumes are not shared between services, so the UI never connects
to SQLite directly.
"""

import os
from typing import Optional

import requests

API_URL = os.getenv("API_URL", "https://web-production-d7d1d.up.railway.app")
_TIMEOUT = 8
_COPILOT_TIMEOUT = 45  # Co-pilot calls invoke Claude — needs longer timeout


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(path: str, **params) -> list | dict:
    try:
        r = requests.get(f"{API_URL}{path}", params={k: v for k, v in params.items() if v is not None}, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[db] GET {path} failed: {e}")
        return [] if path not in ("/metrics",) else {}


def _post(path: str, json: dict | None = None, timeout: int = _TIMEOUT) -> dict:
    try:
        r = requests.post(f"{API_URL}{path}", json=json or {}, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[db] POST {path} failed: {e}")
        return {"ok": False, "error": str(e)}


def _put(path: str, json: dict | None = None, timeout: int = _TIMEOUT) -> dict:
    try:
        r = requests.put(f"{API_URL}{path}", json=json or {}, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[db] PUT {path} failed: {e}")
        return {"ok": False}


def _delete(path: str) -> dict:
    try:
        r = requests.delete(f"{API_URL}{path}", timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[db] DELETE {path} failed: {e}")
        return {"ok": False}


# ── Init (no-op — backend owns the schema) ────────────────────────────────────

def ensure_tables() -> None:
    """No-op: the FastAPI backend creates all tables on startup."""
    pass


# ── Metrics ───────────────────────────────────────────────────────────────────

def get_metrics() -> dict:
    result = _get("/metrics")
    if not isinstance(result, dict):
        result = {}
    return {
        "posts_this_week":  result.get("posts_this_week", 0),
        "draft_count":      result.get("draft_count", 0),
        "pending_comments": result.get("pending_comments", 0),
        "warm_influencers": result.get("warm_influencers", 0),
    }


def get_pending_comment_count() -> int:
    return get_metrics().get("pending_comments", 0)


# ── Content Queue ─────────────────────────────────────────────────────────────

def get_content_queue(status: Optional[str] = None) -> list[dict]:
    result = _get("/content-queue", status=status)
    return result if isinstance(result, list) else []


def update_content_status(row_id: int, status: str) -> None:
    _put(f"/content-queue/{row_id}/status", {"status": status})


def update_content_body(row_id: int, body: str) -> None:
    _put(f"/content-queue/{row_id}", {"body": body})


def delete_content(row_id: int) -> None:
    _delete(f"/content-queue/{row_id}")


# ── Comment Queue ─────────────────────────────────────────────────────────────

def get_comment_queue(status: Optional[str] = None) -> list[dict]:
    result = _get("/comment-queue", status=status)
    return result if isinstance(result, list) else []


def update_comment_status(row_id: int, status: str) -> None:
    _put(f"/comment-queue/{row_id}/status", {"status": status})


def update_comment_text(row_id: int, text: str) -> None:
    _put(f"/comment-queue/{row_id}", {"comment_text": text})


# ── Influencers ───────────────────────────────────────────────────────────────

def get_influencers(status: Optional[str] = None) -> list[dict]:
    result = _get("/influencers", status=status)
    return result if isinstance(result, list) else []


def add_influencer(name: str, linkedin_handle: str, niche: str, notes: str = "") -> None:
    _post("/influencers", {
        "name": name,
        "linkedin_handle": linkedin_handle,
        "niche": niche,
        "notes": notes,
    })


def hibernate_influencer(row_id: int) -> None:
    _put(f"/influencers/{row_id}/hibernate")


def activate_influencer(row_id: int) -> None:
    _put(f"/influencers/{row_id}/activate")


def delete_influencer(row_id: int) -> dict:
    return _delete(f"/influencers/{row_id}")


# ── Discover ──────────────────────────────────────────────────────────────────

def get_discover_suggestions() -> list[dict]:
    result = _get("/discover/suggestions")
    return result if isinstance(result, list) else []


def trigger_discover_generate() -> dict:
    return _post("/discover/generate")


def accept_discover_suggestion(row_id: int) -> dict:
    return _post(f"/discover/suggestions/{row_id}/accept")


def dismiss_discover_suggestion(row_id: int) -> dict:
    return _post(f"/discover/suggestions/{row_id}/dismiss")


def get_discover_pattern() -> dict:
    result = _get("/discover/pattern")
    return result if isinstance(result, dict) else {}


# ── Connections ───────────────────────────────────────────────────────────────

def get_connections(status: Optional[str] = None) -> list[dict]:
    result = _get("/connections", status=status)
    return result if isinstance(result, list) else []


def send_connection(row_id: int) -> dict:
    return _post(f"/connections/{row_id}/send")


def dismiss_connection(row_id: int) -> dict:
    return _post(f"/connections/{row_id}/dismiss")


# ── Feeds ─────────────────────────────────────────────────────────────────────

def get_feeds(priority: Optional[str] = None) -> list[dict]:
    result = _get("/feeds", priority=priority)
    return result if isinstance(result, list) else []


def save_feed(
    name: str,
    url: str,
    feed_type: str,
    priority: str,
    category: str,
    active: int = 1,
) -> None:
    _post("/feeds", {
        "name": name,
        "url": url,
        "feed_type": feed_type,
        "priority": priority,
        "category": category,
        "active": active,
    })


def update_feed(
    row_id: int,
    name: str,
    url: str,
    feed_type: str,
    priority: str,
    category: str,
    active: int,
) -> None:
    _put(f"/feeds/{row_id}", {
        "name": name,
        "url": url,
        "feed_type": feed_type,
        "priority": priority,
        "category": category,
        "active": active,
    })


def toggle_feed_active(row_id: int, active: int) -> None:
    _put(f"/feeds/{row_id}/toggle", {"active": active})


def delete_feed(row_id: int) -> None:
    _delete(f"/feeds/{row_id}")


# ── Strategy ──────────────────────────────────────────────────────────────────

def get_strategy() -> dict:
    result = _get("/strategy")
    return result if isinstance(result, dict) else {}


def update_strategy(data: dict) -> None:
    _put("/strategy", {"data": data})


def get_strategy_health() -> dict:
    result = _get("/strategy/health")
    if not isinstance(result, dict):
        result = {}
    return {
        "comments_today":     result.get("comments_today", 0),
        "max_comments_day":   result.get("max_comments_day", 5),
        "posts_this_week":    result.get("posts_this_week", 0),
        "max_posts_week":     result.get("max_posts_week", 8),
        "topic_distribution": result.get("topic_distribution", {}),
        "target_weights":     result.get("target_weights", {}),
        "archived_this_week": result.get("archived_this_week", 0),
        "flagged_items":      result.get("flagged_items", []),
    }


# ── Analytics ─────────────────────────────────────────────────────────────────

# ── LinkedIn OAuth ─────────────────────────────────────────────────────────────

def get_linkedin_profile() -> dict:
    result = _get("/auth/linkedin/profile")
    if not isinstance(result, dict):
        return {"connected": False}
    return result


def linkedin_logout() -> bool:
    result = _get("/auth/linkedin/logout")
    return isinstance(result, dict) and result.get("success", False)


def score_post(text: str) -> dict:
    result = _post("/analytics/score-post", {"text": text})
    if not isinstance(result, dict):
        result = {}
    return {
        "overall":     result.get("overall", 0),
        "hook":        result.get("hook", 0),
        "data":        result.get("data", 0),
        "readability": result.get("readability", 0),
        "cta":         result.get("cta", 0),
        "suggestion":  result.get("suggestion", ""),
    }


# ── Topics ─────────────────────────────────────────────────────────────────────

def get_topics() -> list[dict]:
    result = _get("/topics")
    return result if isinstance(result, list) else []


def toggle_topic_active(row_id: int) -> dict:
    return _put(f"/topics/{row_id}/toggle")


def rebalance_topics() -> dict:
    return _put("/topics/rebalance")


def delete_topic(row_id: int) -> dict:
    return _delete(f"/topics/{row_id}")


def start_topic_copilot(user_message: str) -> dict:
    result = _post("/topics/copilot/start", {"user_message": user_message}, timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def message_topic_copilot(conv_id: int, user_message: str) -> dict:
    result = _post(f"/topics/copilot/{conv_id}/message", {"user_message": user_message}, timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def confirm_topic_copilot(conv_id: int) -> dict:
    result = _post(f"/topics/copilot/{conv_id}/confirm", timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


# ── ICP ────────────────────────────────────────────────────────────────────────

def get_icp() -> dict:
    result = _get("/icp")
    return result if isinstance(result, dict) else {"exists": False}


def delete_icp() -> dict:
    return _delete("/icp")


def start_icp_copilot(user_message: str) -> dict:
    result = _post("/icp/copilot/start", {"user_message": user_message}, timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def message_icp_copilot(conv_id: int, user_message: str) -> dict:
    result = _post(f"/icp/copilot/{conv_id}/message", {"user_message": user_message}, timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def confirm_icp_copilot(conv_id: int) -> dict:
    result = _post(f"/icp/copilot/{conv_id}/confirm", timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


# ── Voice Profile ───────────────────────────────────────────────────────────────

def get_voice_profile() -> dict:
    result = _get("/voice-profile")
    return result if isinstance(result, dict) else {"exists": False}


def delete_voice_profile() -> dict:
    return _delete("/voice-profile")


def get_voice_history() -> list[dict]:
    result = _get("/voice-profile/history")
    return result if isinstance(result, list) else []


def accept_voice_change(row_id: int) -> dict:
    return _put(f"/voice-profile/history/{row_id}/accept")


def reject_voice_change(row_id: int) -> dict:
    return _put(f"/voice-profile/history/{row_id}/reject")


def start_voice_copilot(user_message: str) -> dict:
    result = _post("/voice-profile/copilot/start", {"user_message": user_message}, timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def message_voice_copilot(conv_id: int, user_message: str) -> dict:
    result = _post(f"/voice-profile/copilot/{conv_id}/message", {"user_message": user_message}, timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def confirm_voice_copilot(conv_id: int) -> dict:
    result = _post(f"/voice-profile/copilot/{conv_id}/confirm", timeout=_COPILOT_TIMEOUT)
    return result if isinstance(result, dict) else {"ok": False}


def trigger_analyze_edits() -> dict:
    return _post("/voice-profile/analyze-edits")
