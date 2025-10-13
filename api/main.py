# api/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict, Any

from api.handlers.build_handler import handle_build_request

# Load environment variables (from .env)
load_dotenv()

# Create FastAPI app
app = FastAPI(title="LLM Code Deployment API")

# Get secret from environment
STUDENT_SECRET = os.getenv("STUDENT_SECRET")


# Define the expected request structure
class RequestPayload(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: Optional[str] = None
    checks: Optional[List[str]] = None
    evaluation_url: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


@app.post("/")
async def handle_request(payload: RequestPayload, request: Request):
    """
    Handles the instructor's POST request.
    1. Verifies secret.
    2. Routes round 1 requests to build_handler.
    """

    # Step 1: Verify secret
    if payload.secret != STUDENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # Step 2: Log received task
    print(f"Received task '{payload.task}' (round {payload.round}) from {payload.email}")

    # Step 3: Handle Build (round 1) — extend later for revise (round 2)
    if payload.round == 1:
        response = handle_build_request(payload)
    else:
        response = {
            "status": "error",
            "message": f"Round {payload.round} not implemented yet"
        }

    return JSONResponse(status_code=200, content=response)


@app.get("/health")
async def health():
    """Simple health check endpoint"""
    return {"status": "alive"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)