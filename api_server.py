from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database

app = FastAPI(title="Coder-Bot Web Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BanRequest(BaseModel):
    discord_id: str
    reason: str = "Banned from Web Dashboard"

@app.get("/api/stats")
async def get_stats():
    return database.get_dashboard_stats()

@app.post("/api/ban")
async def ban_user(data: BanRequest):
    database.ban_user(data.discord_id, data.reason)
    return {"status": "success", "message": f"User {data.discord_id} banned."}

@app.post("/api/unban")
async def unban_user(data: BanRequest):
    database.unban_user(data.discord_id)
    return {"status": "success", "message": f"User {data.discord_id} unbanned."}

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Coder-Bot Admin Dashboard</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
            h1, h2 { color: #38bdf8; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
            .card { background: #1e293b; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
            .stat-num { font-size: 2rem; font-weight: bold; color: #38bdf8; }
            table { width: 100%; border-collapse: collapse; margin-top: 1rem; background: #1e293b; border-radius: 8px; overflow: hidden; }
            th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
            th { background: #0f172a; color: #94a3b8; }
            .ban-btn { background: #ef4444; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; }
            .unban-btn { background: #10b981; color: white; border: none; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; }
            input { padding: 0.5rem; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>🎛️ Coder-Bot Control Panel</h1>
        
        <div class="grid">
            <div class="card"><div>Total Prompts</div><div class="stat-num" id="totalPrompts">0</div></div>
            <div class="card"><div>Unique Users</div><div class="stat-num" id="uniqueUsers">0</div></div>
            <div class="card"><div>Banned Users</div><div class="stat-num" id="bannedCount">0</div></div>
        </div>

        <h2>🚫 Quick User Ban</h2>
        <div class="card" style="display:flex; gap: 0.5rem; max-width: 500px;">
            <input type="text" id="banId" placeholder="Discord User ID" style="flex: 1;">
            <button class="ban-btn" onclick="banUserManual()">Ban User</button>
        </div>

        <h2>📜 Recent Prompt History</h2>
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>User</th>
                    <th>Server</th>
                    <th>Prompt</th>
                    <th>Response</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="promptTable"></tbody>
        </table>

        <script>
            async function loadData() {
                const res = await fetch('/api/stats');
                const data = await res.json();

                document.getElementById('totalPrompts').innerText = data.total_prompts;
                document.getElementById('uniqueUsers').innerText = data.unique_users;
                document.getElementById('bannedCount').innerText = data.banned_count;

                const tbody = document.getElementById('promptTable');
                tbody.innerHTML = '';
                data.recent_prompts.forEach(p => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${p.time}</td>
                            <td><b>${p.username}</b><br><small>${p.user_id}</small></td>
                            <td>${p.server}</td>
                            <td>${p.prompt}</td>
                            <td>${p.response.substring(0, 50)}...</td>
                            <td><button class="ban-btn" onclick="banUser('${p.user_id}')">Ban</button></td>
                        </tr>
                    `;
                });
            }

            async function banUser(userId) {
                if(!confirm(`Ban user ID ${userId}?`)) return;
                await fetch('/api/ban', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ discord_id: userId })
                });
                loadData();
            }

            async function banUserManual() {
                const id = document.getElementById('banId').value.trim();
                if(id) {
                    await banUser(id);
                    document.getElementById('banId').value = '';
                }
            }

            loadData();
            setInterval(loadData, 5000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
