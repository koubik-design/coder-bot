import sqlite3
import secrets
DB_PATH = "coder_bot.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    api_key TEXT UNIQUE
                 )''')
    conn.commit()
    conn.close()
def generate_key(user_id, username):
    """Generates and stores a key instantly."""
    new_key = f"cb-{secrets.token_hex(16)}"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users (user_id, username, api_key) 
                 VALUES (?, ?, ?)''', (str(user_id), str(username), new_key))
    conn.commit()
    conn.close()
    return new_key
def verify_key(api_key):
    """Checks if key exists and returns user info."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users WHERE api_key = ?", (api_key,))
    res = c.fetchone()
    conn.close()
    return res
init_db()
