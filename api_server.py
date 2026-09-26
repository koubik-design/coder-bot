import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import database
from utils import call_ai                                     
app = FastAPI(title="Coder-Bot Backend")
class AskReq(BaseModel): prompt: str
class CodeReq(BaseModel): language: str; prompt: str
class DebugReq(BaseModel): language: str; code: str
async def verify(api_key: str | None = None, authorization: str | None = None):
    if not api_key and authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer":
            api_key = value.strip()
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
async def ask_api(req: AskReq, x_api_key: str | None = Header(None), authorization: str | None = Header(None)):
    await verify(x_api_key, authorization)
    sys_p = "You are Coder, an expert technical consultant. Answer clearly and concisely."
    res = await call_ai(sys_p, req.prompt)
    return {"response": res}                                 
@app.post("/code")
async def code_api(req: CodeReq, x_api_key: str | None = Header(None), authorization: str | None = Header(None)):
    await verify(x_api_key, authorization)
    sys_p = f"You are an expert {req.language} developer."
    res = await call_ai(sys_p, req.prompt)
    return {"response": res}
@app.post("/plan")
async def plan_api(req: AskReq, x_api_key: str | None = Header(None), authorization: str | None = Header(None)):
    await verify(x_api_key, authorization)
    sys_p = "You are an expert system architect. Provide a structured step-by-step roadmap."
    res = await call_ai(sys_p, req.prompt)
    return {"response": res}
@app.post("/debug")
async def debug_api(req: DebugReq, x_api_key: str | None = Header(None), authorization: str | None = Header(None)):
    await verify(x_api_key, authorization)
    sys_p = f"Find errors and provide fixed {req.language} code."
    res = await call_ai(sys_p, req.code)
    return {"response": res}
@app.post("/verify-key")
async def verify_key(req: dict):
    user = await verify(req.get("api_key"))
    return {"user": {"discord_id": user[0], "username": user[1]}}
if __name__ == "__main__":
    print(" Starting Coder API Server on port 8000...")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
