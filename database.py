import sqlite3
import secrets
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "coder_bot.db"

def init_db():
    """Initialize database tables for users and API keys."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def generate_api_key(discord_id: str, username: str) -> str:
    """Generate or retrieve a unique API key for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user already has a key
    cursor.execute("SELECT api_key FROM users WHERE discord_id = ?", (discord_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]

    # Generate a new token format: coder-<random_hex>
    new_key = f"coder-{secrets.token_hex(16)}"
    
    cursor.execute(
        "INSERT INTO users (discord_id, username, api_key) VALUES (?, ?, ?)",
        (discord_id, username, new_key)
    )
    conn.commit()
    conn.close()
    return new_key

def verify_api_key(api_key: str) -> dict | None:
    """Verify an API key and return user data if valid."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT discord_id, username FROM users WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"discord_id": row[0], "username": row[1]}
    return None

# Auto-initialize DB on import
init_db()
