# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests
import os

from rag import process_document, ask_question

app = FastAPI()

# CORS для React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    model: str = "mistral:7b-instruct"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"../documents/{file.filename}"
    os.makedirs("../documents", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    process_document(file_path)
    return {"filename": file.filename, "status": "processed"}

@app.post("/ask")
async def ask(request: QuestionRequest):
    answer = ask_question(request.question, request.model)
    return {"answer": answer}

@app.get("/models")
async def list_models():
    return {
        "available": [
            "nomic-embed-text",
            "mistral:7b-instruct",
            "qwen2:0.5b-instruct"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)