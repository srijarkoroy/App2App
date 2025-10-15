# api/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict, Any

from api.handlers.build_handler import handle_build_request
from api.handlers.revise_handler import handle_revise_request

# Load environment variables (for local development)
load_dotenv()

# Create FastAPI app
app = FastAPI(title="LLM Code Deployment API")

# Secret from environment
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

    # Verify secret
    if payload.secret != STUDENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # Log received task
    print(f"Received task '{payload.task}' (round {payload.round}) from {payload.email}")

    # Handle Build (round 1)
    if payload.round == 1:
        response = handle_build_request(payload)
        
    # Handle Revise (round 2)
    elif payload.round == 2:
        response = handle_revise_request(payload)

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

    # Use PORT environment variable if available (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
