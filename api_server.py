from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database

app = FastAPI(title="Coder-Bot API")

# Enable CORS for GitHub Pages requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from your GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class KeyValidationRequest(BaseModel):
    api_key: str

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"status": "online", "message": "Coder-Bot Backend Operational"}

@app.post("/verify-key")
async def verify_key(data: KeyValidationRequest):
    user = database.verify_api_key(data.api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return {"valid": True, "user": user}

@app.post("/ask")
async def ask_endpoint(payload: PromptRequest, x_api_key: str = Header(...)):
    user = database.verify_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or Missing API Key")
    
    # Process request for valid user
    return {
        "status": "success",
        "user": user["username"],
        "reply": f"Hello {user['username']}, received your prompt: '{payload.prompt}'"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
