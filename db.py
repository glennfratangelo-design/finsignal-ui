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


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(path: str, **params) -> list | dict:
    try:
        r = requests.get(f"{API_URL}{path}", params={k: v for k, v in params.items() if v is not None}, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[db] GET {path} failed: {e}")
        return [] if path not in ("/metrics",) else {}


def _post(path: str, json: dict | None = None) -> dict:
    try:
        r = requests.post(f"{API_URL}{path}", json=json or {}, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[db] POST {path} failed: {e}")
        return {"ok": False}


def _put(path: str, json: dict | None = None) -> dict:
    try:
        r = requests.put(f"{API_URL}{path}", json=json or {}, timeout=_TIMEOUT)
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

def get_influencers(
    search: Optional[str] = None,
    niches: Optional[list] = None,
    relationships: Optional[list] = None,
) -> list[dict]:
    params: dict = {}
    if search:
        params["search"] = search
    if niches:
        params["niches"] = ",".join(niches)
    if relationships:
        params["relationships"] = ",".join(relationships)
    result = _get("/influencers", **params)
    return result if isinstance(result, list) else []


def add_influencer(
    name: str,
    linkedin_url: str,
    handle: str,
    niche: str,
    follower_count: int,
    relationship: str,
) -> None:
    _post("/influencers", {
        "name": name,
        "linkedin_url": linkedin_url,
        "handle": handle,
        "niche": niche,
        "follower_count": follower_count,
        "relationship": relationship,
    })


def update_influencer_relationship(row_id: int, relationship: str) -> None:
    _put(f"/influencers/{row_id}/relationship", {"relationship": relationship})


def log_influencer_interaction(row_id: int) -> None:
    _put(f"/influencers/{row_id}/interact")


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
