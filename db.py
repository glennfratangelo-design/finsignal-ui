"""
SQLite helper layer for FinSignal UI.
Connects to the same persistent volume as the FastAPI backend.
"""

import os
import sqlite3
from typing import Optional

DB_PATH = os.getenv("DATABASE_URL", "/data/finsignal.db")

SEED_INFLUENCERS = [
    {"name": "Karisse Hendrick",    "linkedin_url": "https://www.linkedin.com/in/karissehendrick/",                    "niche": "Fraud",     "follower_count": 12000},
    {"name": "Frank McKenna",       "linkedin_url": "https://www.linkedin.com/in/frankmckenna/",                       "niche": "Fraud",     "follower_count": 45000},
    {"name": "D.O. Turner",         "linkedin_url": "https://www.linkedin.com/in/doturner/",                           "niche": "AML",       "follower_count": 8000},
    {"name": "Mam Samba",           "linkedin_url": "https://www.linkedin.com/in/cybergalmam/",                        "niche": "AML",       "follower_count": 7500},
    {"name": "Debra Geister",       "linkedin_url": "https://www.linkedin.com/in/debra-geister-aml-fincrime/",         "niche": "AML",       "follower_count": 9200},
    {"name": "Steve Lenderman",     "linkedin_url": "https://www.linkedin.com/in/steve-lenderman/",                    "niche": "KYC",       "follower_count": 6800},
    {"name": "Dana Lawrence",       "linkedin_url": "https://www.linkedin.com/in/danalawrencefintech/",                "niche": "RegTech",   "follower_count": 11000},
    {"name": "Becky Reed",          "linkedin_url": "https://www.linkedin.com/in/becky-reed-50056518/",                "niche": "AML",       "follower_count": 5500},
    {"name": "John Wingate",        "linkedin_url": "https://www.linkedin.com/in/johnwingate/",                        "niche": "KYC",       "follower_count": 7200},
    {"name": "Mike Cook",           "linkedin_url": "https://www.linkedin.com/in/mike-cook-2b41245/",                  "niche": "Fraud",     "follower_count": 8900},
    {"name": "Ari Redbord",         "linkedin_url": "https://www.linkedin.com/in/ari-redbord/",                        "niche": "Crypto",    "follower_count": 28000},
    {"name": "Ian Mitchell",        "linkedin_url": "https://www.linkedin.com/in/iantmitchell/",                       "niche": "RegTech",   "follower_count": 15000},
    {"name": "John Tipper",         "linkedin_url": "https://www.linkedin.com/in/tipperx/",                            "niche": "AML",       "follower_count": 6200},
    {"name": "Matt O'Neill",        "linkedin_url": "https://www.linkedin.com/in/matt-o%E2%80%99neill-5b1b4b172/",    "niche": "Fraud",     "follower_count": 9800},
    {"name": "Stephen Sargeant",    "linkedin_url": "https://www.linkedin.com/in/stephen-brent-sargeant-cams/",        "niche": "AML",       "follower_count": 7100},
    {"name": "Ken Palla",           "linkedin_url": "https://www.linkedin.com/in/ken-palla-09b585/",                   "niche": "Fraud",     "follower_count": 5900},
    {"name": "Jen Lamont",          "linkedin_url": "https://www.linkedin.com/in/jen-lamont-cbsap-cfe-22a561103/",    "niche": "KYC",       "follower_count": 4800},
    {"name": "Karen Boyer",         "linkedin_url": "https://www.linkedin.com/in/karen-boyer-cfe-cfci-ccci-0478b523/","niche": "Fraud",     "follower_count": 6300},
    {"name": "Erin Vertin",         "linkedin_url": "https://www.linkedin.com/in/erin-vertin/",                        "niche": "AML",       "follower_count": 5100},
    {"name": "Angela Diaz",         "linkedin_url": "https://www.linkedin.com/in/angela-diaz-crmp-37430064/",          "niche": "Sanctions", "follower_count": 4200},
    {"name": "Justin Davis",        "linkedin_url": "https://www.linkedin.com/in/justin-davis-cfe/",                   "niche": "Fraud",     "follower_count": 7800},
    {"name": "Michael Timoney",     "linkedin_url": "https://www.linkedin.com/in/michael-timoney/",                    "niche": "RegTech",   "follower_count": 6600},
    {"name": "Nyla D. Cortes",      "linkedin_url": "https://www.linkedin.com/in/nyla-d-cortes/",                      "niche": "KYC",       "follower_count": 5400},
    {"name": "Oonagh van den Berg", "linkedin_url": "https://www.linkedin.com/in/oonagh-van-den-berg/",                "niche": "AML",       "follower_count": 19000},
    {"name": "Ronald Pol",          "linkedin_url": "https://www.linkedin.com/in/ronaldpol/",                          "niche": "AML",       "follower_count": 16000},
    {"name": "Kieran Beer",         "linkedin_url": "https://www.linkedin.com/in/kieranbeer/",                         "niche": "AML",       "follower_count": 14000},
    {"name": "Branislav Horak",     "linkedin_url": "https://www.linkedin.com/in/branislavhorak/",                     "niche": "Fraud",     "follower_count": 8400},
    {"name": "Adam McLaughlin",     "linkedin_url": "https://www.linkedin.com/in/adam-mclaughlin-4a269031/",           "niche": "AML",       "follower_count": 11500},
    {"name": "Seb Taylor",          "linkedin_url": "https://www.linkedin.com/in/sytaylor/",                           "niche": "RegTech",   "follower_count": 22000},
    {"name": "Jim Mortensen",       "linkedin_url": "https://www.linkedin.com/in/jimrmortensen/",                      "niche": "Fraud",     "follower_count": 7300},
    {"name": "Trace Fooshee",       "linkedin_url": "https://www.linkedin.com/in/trace-foosh%C3%A9e-8441a51/",        "niche": "AML",       "follower_count": 9600},
    {"name": "Julie Conroy",        "linkedin_url": "https://www.linkedin.com/in/julie-conroy-6997/",                  "niche": "Fraud",     "follower_count": 18000},
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
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                post_url     TEXT,
                comment_text TEXT,
                status       TEXT DEFAULT 'pending',
                created_at   TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS influencers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                linkedin_url    TEXT UNIQUE,
                niche           TEXT,
                follower_count  INTEGER DEFAULT 0,
                relationship    TEXT DEFAULT 'Cold',
                last_interacted TEXT,
                created_at      TEXT DEFAULT (datetime('now'))
            );
        """)
        count = conn.execute("SELECT COUNT(*) FROM influencers").fetchone()[0]
        if count == 0:
            conn.executemany(
                """INSERT OR IGNORE INTO influencers (name, linkedin_url, niche, follower_count)
                   VALUES (:name, :linkedin_url, :niche, :follower_count)""",
                SEED_INFLUENCERS,
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
            "SELECT COUNT(*) FROM influencers WHERE relationship = 'Warm'"
        ).fetchone()[0]
    return {
        "posts_this_week":  posts_this_week,
        "draft_count":      draft_count,
        "pending_comments": pending_comments,
        "warm_influencers": warm_influencers,
        "avg_engagement":   0.0,  # populated when LinkedIn API returns engagement data
    }


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

def get_influencers(search: Optional[str] = None) -> list[dict]:
    with _conn() as conn:
        if search:
            rows = conn.execute(
                """SELECT * FROM influencers
                   WHERE name LIKE ? OR niche LIKE ?
                   ORDER BY follower_count DESC""",
                (f"%{search}%", f"%{search}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM influencers ORDER BY follower_count DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def add_influencer(name: str, linkedin_url: str, niche: str, follower_count: int, relationship: str) -> None:
    with _conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO influencers (name, linkedin_url, niche, follower_count, relationship)
               VALUES (?, ?, ?, ?, ?)""",
            (name, linkedin_url, niche, follower_count, relationship),
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
