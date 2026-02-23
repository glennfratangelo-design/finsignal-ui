"""
SQLite helper layer for FinSignal UI.
Connects to the same persistent volume as the FastAPI backend.
"""

import os
import sqlite3
from typing import Optional

DB_PATH = os.getenv("DATABASE_URL", "/data/finsignal.db")

SEED_INFLUENCERS = [
    {"name": "Tom Schofield",         "handle": "tomschofield_aml",        "niche": "AML",       "follower_count": 0},
    {"name": "Kieran Beer",            "handle": "kieranbeer",              "niche": "AML",       "follower_count": 0},
    {"name": "John Cassara",           "handle": "johncassara",             "niche": "AML",       "follower_count": 0},
    {"name": "Debra Geister",          "handle": "debrageister",            "niche": "AML",       "follower_count": 0},
    {"name": "Jason Meents",           "handle": "jasonmeents",             "niche": "KYC",       "follower_count": 0},
    {"name": "Nick Maxwell",           "handle": "nickmaxwell_fincrime",    "niche": "Fraud",     "follower_count": 0},
    {"name": "Kristy Grant-Hart",      "handle": "kristygranthart",         "niche": "Sanctions", "follower_count": 0},
    {"name": "Jimmy Fong",             "handle": "jimmyfong_aml",           "niche": "AML",       "follower_count": 0},
    {"name": "David Schwartz",         "handle": "davidschwartz_fatf",      "niche": "RegTech",   "follower_count": 0},
    {"name": "Ari Redbord",            "handle": "ariredbord",              "niche": "Fraud",     "follower_count": 0},
    {"name": "Carole House",           "handle": "carolehouse",             "niche": "AML",       "follower_count": 0},
    {"name": "Jennifer Shasky Calvery","handle": "jenshaskycalvery",        "niche": "AML",       "follower_count": 0},
    {"name": "Peter Hardy",            "handle": "peterhardy_aml",          "niche": "AML",       "follower_count": 0},
    {"name": "Ross Delston",           "handle": "rossdelston",             "niche": "AML",       "follower_count": 0},
    {"name": "Mary Holt",              "handle": "maryholt_compliance",     "niche": "KYC",       "follower_count": 0},
    {"name": "Brian Monroe",           "handle": "brianmonroe_acams",       "niche": "AML",       "follower_count": 0},
    {"name": "Chuck Taylor",           "handle": "chucktaylor_aml",         "niche": "AML",       "follower_count": 0},
    {"name": "Alma Angotti",           "handle": "almaangotti",             "niche": "Sanctions", "follower_count": 0},
    {"name": "Gary Kalman",            "handle": "garykalman",              "niche": "AML",       "follower_count": 0},
    {"name": "Liat Shetret",           "handle": "liatshetret",             "niche": "Sanctions", "follower_count": 0},
    {"name": "Yaya Fanusie",           "handle": "yayafanusie",             "niche": "AML",       "follower_count": 0},
    {"name": "Michael McDonald",       "handle": "michaelmcdonald_kyc",     "niche": "KYC",       "follower_count": 0},
    {"name": "Giles Crown",            "handle": "gilescrown",              "niche": "RegTech",   "follower_count": 0},
    {"name": "Andrew Downer",          "handle": "andrewdowner_aml",        "niche": "AML",       "follower_count": 0},
    {"name": "Fran Lawler",            "handle": "franlawler",              "niche": "Fraud",     "follower_count": 0},
    {"name": "John Tobon",             "handle": "johntobon_doj",           "niche": "AML",       "follower_count": 0},
    {"name": "Lisa Arquette",          "handle": "lisaarquette_ffiec",      "niche": "RegTech",   "follower_count": 0},
    {"name": "Brian Kindle",           "handle": "briankindle_acams",       "niche": "AML",       "follower_count": 0},
    {"name": "Sharon Cohen Levin",     "handle": "sharoncohenlevin",        "niche": "AML",       "follower_count": 0},
    {"name": "Kieran Flynn",           "handle": "kieranflynn_regtech",     "niche": "RegTech",   "follower_count": 0},
    {"name": "Nina Schick",            "handle": "ninaschick_ai",           "niche": "RegTech",   "follower_count": 0},
    {"name": "Mike Benz",              "handle": "mikebenz_fincrime",       "niche": "Fraud",     "follower_count": 0},
]


# ── Connection ────────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    except Exception:
        pass
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ── Init ──────────────────────────────────────────────────────────────────────

def ensure_tables() -> None:
    """Create UI-owned tables and seed data if needed. Safe to call on every startup."""
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS content_queue (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT,
                body       TEXT,
                status     TEXT DEFAULT 'draft',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS comment_queue (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                post_url        TEXT,
                influencer_name TEXT,
                post_snippet    TEXT,
                comment_text    TEXT,
                status          TEXT DEFAULT 'pending',
                created_at      TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS influencers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                linkedin_url    TEXT UNIQUE,
                handle          TEXT,
                niche           TEXT,
                follower_count  INTEGER DEFAULT 0,
                relationship    TEXT DEFAULT 'Cold',
                last_interacted TEXT,
                created_at      TEXT DEFAULT (datetime('now'))
            );
        """)
        # Add missing columns to existing tables (idempotent migrations)
        try:
            conn.execute("ALTER TABLE comment_queue ADD COLUMN influencer_name TEXT")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE comment_queue ADD COLUMN post_snippet TEXT")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE influencers ADD COLUMN handle TEXT")
        except Exception:
            pass

        count = conn.execute("SELECT COUNT(*) FROM influencers").fetchone()[0]
        if count == 0:
            conn.executemany(
                """INSERT OR IGNORE INTO influencers (name, linkedin_url, handle, niche, follower_count)
                   VALUES (:name, :linkedin_url, :handle, :niche, :follower_count)""",
                [
                    {
                        **inf,
                        "linkedin_url": f"https://www.linkedin.com/in/{inf['handle']}/",
                    }
                    for inf in SEED_INFLUENCERS
                ],
            )


# ── Metrics ───────────────────────────────────────────────────────────────────

def get_metrics() -> dict:
    with _conn() as conn:
        posts_this_week = conn.execute(
            "SELECT COUNT(*) FROM content_queue WHERE created_at >= datetime('now', '-7 days')"
        ).fetchone()[0]
        draft_count = conn.execute(
            "SELECT COUNT(*) FROM content_queue WHERE status = 'draft'"
        ).fetchone()[0]
        pending_comments = conn.execute(
            "SELECT COUNT(*) FROM comment_queue WHERE status = 'pending'"
        ).fetchone()[0]
        warm_influencers = conn.execute(
            "SELECT COUNT(*) FROM influencers WHERE relationship IN ('Warm', 'Connected', 'Partner')"
        ).fetchone()[0]
    return {
        "posts_this_week":  posts_this_week,
        "draft_count":      draft_count,
        "pending_comments": pending_comments,
        "warm_influencers": warm_influencers,
    }


def get_pending_comment_count() -> int:
    with _conn() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM comment_queue WHERE status = 'pending'"
        ).fetchone()[0]


# ── Content Queue ─────────────────────────────────────────────────────────────

def get_content_queue(status: Optional[str] = None) -> list[dict]:
    with _conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM content_queue WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM content_queue ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def update_content_status(row_id: int, status: str) -> None:
    with _conn() as conn:
        conn.execute("UPDATE content_queue SET status = ? WHERE id = ?", (status, row_id))


def update_content_body(row_id: int, body: str) -> None:
    with _conn() as conn:
        conn.execute("UPDATE content_queue SET body = ? WHERE id = ?", (body, row_id))


def delete_content(row_id: int) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM content_queue WHERE id = ?", (row_id,))


# ── Comment Queue ─────────────────────────────────────────────────────────────

def get_comment_queue(status: Optional[str] = None) -> list[dict]:
    with _conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM comment_queue WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM comment_queue ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def update_comment_status(row_id: int, status: str) -> None:
    with _conn() as conn:
        conn.execute("UPDATE comment_queue SET status = ? WHERE id = ?", (status, row_id))


def update_comment_text(row_id: int, text: str) -> None:
    with _conn() as conn:
        conn.execute("UPDATE comment_queue SET comment_text = ? WHERE id = ?", (text, row_id))


# ── Influencers ───────────────────────────────────────────────────────────────

def get_influencers(
    search: Optional[str] = None,
    niches: Optional[list] = None,
    relationships: Optional[list] = None,
) -> list[dict]:
    with _conn() as conn:
        query = "SELECT * FROM influencers WHERE 1=1"
        params: list = []

        if search:
            query += " AND (name LIKE ? OR niche LIKE ? OR handle LIKE ?)"
            params += [f"%{search}%", f"%{search}%", f"%{search}%"]

        if niches:
            placeholders = ",".join("?" * len(niches))
            query += f" AND niche IN ({placeholders})"
            params += niches

        if relationships:
            placeholders = ",".join("?" * len(relationships))
            query += f" AND relationship IN ({placeholders})"
            params += relationships

        query += " ORDER BY follower_count DESC, name ASC"
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def add_influencer(name: str, linkedin_url: str, handle: str, niche: str, follower_count: int, relationship: str) -> None:
    with _conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO influencers (name, linkedin_url, handle, niche, follower_count, relationship)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, linkedin_url, handle, niche, follower_count, relationship),
        )


def update_influencer_relationship(row_id: int, relationship: str) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE influencers SET relationship = ?, last_interacted = datetime('now') WHERE id = ?",
            (relationship, row_id),
        )


def log_influencer_interaction(row_id: int) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE influencers SET last_interacted = datetime('now') WHERE id = ?",
            (row_id,),
        )
