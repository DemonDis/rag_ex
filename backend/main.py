# backend/main.py

from fastapi import FastAPI, UploadFile, File, Request, Response
from pydantic import BaseModel
import uvicorn
import os

from rag import process_document, ask_question

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str
    model: str = "mistral:7b-instruct"

# ✅ Разрешённые домены — с учётом слешей
ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "http://localhost:3000/",
    "http://localhost:5173",
    "http://localhost:5173/",
}

# ✅ OPTIONS /api/ask — ручная обработка
@app.options("/api/ask")
async def options_ask(request: Request):
    origin = request.headers.get("origin")
    if origin in ALLOWED_ORIGINS:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
        return Response(content="", headers=headers)
    else:
        return Response(content="Forbidden", status_code=403)

# ✅ POST /api/ask — ручная обработка с динамическим Origin
@app.post("/api/ask")
async def ask(request: QuestionRequest, req: Request):
    origin = req.headers.get("origin")
    if origin not in ALLOWED_ORIGINS:
        return Response(
            content='{"error": "CORS origin not allowed"}',
            media_type="application/json",
            status_code=403
        )

    answer = ask_question(request.question, request.model)

    headers = {
        "Access-Control-Allow-Origin": origin,  # ✅ ДИНАМИЧЕСКИЙ — совпадает с реальным Origin
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }

    return Response(
        content=f'{{"answer": "{answer}"}}',
        media_type="application/json",
        headers=headers,
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), req: Request = None):
    file_path = f"../documents/{file.filename}"
    os.makedirs("../documents", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    process_document(file_path)

    origin = req.headers.get("origin") if req else None
    if origin not in ALLOWED_ORIGINS:
        origin = "http://localhost:5173"  # fallback

    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }

    return Response(
        content=f'{{"filename": "{file.filename}", "status": "processed"}}',
        media_type="application/json",
        headers=headers,
    )

@app.get("/models")
async def list_models(req: Request):
    origin = req.headers.get("origin")
    if origin not in ALLOWED_ORIGINS:
        origin = "http://localhost:5173"  # fallback

    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }

    return Response(
        content='{"available": ["nomic-embed-text", "mistral:7b-instruct", "qwen2:0.5b-instruct"]}',
        media_type="application/json",
        headers=headers,
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)