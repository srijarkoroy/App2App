from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Local Evaluation Server")

@app.post("/notify")
async def receive_notification(payload: dict):
    print("Received notification from student API:")
    print(payload)
    return JSONResponse(status_code=200, content={"status": "ok", "message": "Notification received"})

@app.get("/health")
async def health():
    return {"status": "alive"}
