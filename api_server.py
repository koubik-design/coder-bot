import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import database
from utils import call_ai  # Pulls your AI logic from utils.py

app = FastAPI(title="Coder-Bot Backend")

# Define Data Models expected from CLI
class AskReq(BaseModel): prompt: str
class CodeReq(BaseModel): language: str; prompt: str
class DebugReq(BaseModel): language: str; code: str

# Fast Authentication Checker
async def verify(api_key: str):
    if not api_key: 
        raise HTTPException(status_code=401, detail="Missing API Key")
    user = database.verify_key(api_key)
    if not user: 
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user

@app.get("/status")
async def status():
    return {"status": "online"}

@app.post("/ask")
async def ask_api(req: AskReq, x_api_key: str = Header(None)):
    await verify(x_api_key)
    sys_p = "You are Coder, an expert technical consultant. Answer clearly and concisely."
    res = await call_ai(sys_p, req.prompt)
    return {"response": res} # Returns the AI text to the CLI

@app.post("/code")
async def code_api(req: CodeReq, x_api_key: str = Header(None)):
    await verify(x_api_key)
    sys_p = f"You are an expert {req.language} developer."
    res = await call_ai(sys_p, req.prompt)
    return {"response": res}

@app.post("/plan")
async def plan_api(req: AskReq, x_api_key: str = Header(None)):
    await verify(x_api_key)
    sys_p = "You are an expert system architect. Provide a structured step-by-step roadmap."
    res = await call_ai(sys_p, req.prompt)
    return {"response": res}

@app.post("/debug")
async def debug_api(req: DebugReq, x_api_key: str = Header(None)):
    await verify(x_api_key)
    sys_p = f"Find errors and provide fixed {req.language} code."
    res = await call_ai(sys_p, req.code)
    return {"response": res}

if __name__ == "__main__":
    print("🚀 Starting Coder API Server on port 8000...")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
