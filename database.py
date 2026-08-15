import sqlite3
import secrets
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "coder_bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Banned users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banned_users (
            discord_id TEXT PRIMARY KEY,
            reason TEXT DEFAULT 'Banned by Admin',
            banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Prompt History Log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT NOT NULL,
            username TEXT NOT NULL,
            server_name TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def generate_api_key(discord_id: str, username: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT api_key FROM users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]

    new_key = f"coder-{secrets.token_hex(16)}"
    cursor.execute(
        "INSERT INTO users (discord_id, username, api_key) VALUES (?, ?, ?)",
        (discord_id, username, new_key)
    )
    conn.commit()
    conn.close()
    return new_key

def verify_api_key(api_key: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id, username FROM users WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    return {"discord_id": row[0], "username": row[1]} if row else None

# --- Ban Management ---
def ban_user(discord_id: str, reason: str = "Banned via Dashboard") -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO banned_users (discord_id, reason) VALUES (?, ?)", (discord_id, reason))
    conn.commit()
    conn.close()
    return True

def unban_user(discord_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM banned_users WHERE discord_id = ?", (discord_id,))
    conn.commit()
    conn.close()
    return True

def is_user_banned(discord_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM banned_users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# --- Logging & Stats ---
def log_prompt(discord_id: str, username: str, server_name: str, prompt: str, response: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prompt_logs (discord_id, username, server_name, prompt, response) VALUES (?, ?, ?, ?, ?)",
        (discord_id, username, server_name, prompt, response)
    )
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM prompt_logs")
    total_prompts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT discord_id) FROM prompt_logs")
    unique_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM banned_users")
    banned_count = cursor.fetchone()[0]

    cursor.execute("SELECT discord_id, username, server_name, prompt, response, created_at FROM prompt_logs ORDER BY id DESC LIMIT 50")
    recent_prompts = [
        {"user_id": r[0], "username": r[1], "server": r[2], "prompt": r[3], "response": r[4], "time": r[5]}
        for r in cursor.fetchall()
    ]

    cursor.execute("SELECT discord_id, reason, banned_at FROM banned_users")
    banned_list = [{"user_id": r[0], "reason": r[1], "time": r[2]} for r in cursor.fetchall()]

    conn.close()
    return {
        "total_prompts": total_prompts,
        "unique_users": unique_users,
        "banned_count": banned_count,
        "recent_prompts": recent_prompts,
        "banned_users": banned_list
    }

init_db()
