# backend/rag.py

import re
from rank_bm25 import BM25Okapi
from utils import extract_text
from vector_store import save_chunks, load_chunks
import requests

OLLAMA_API = "http://localhost:11434/api/generate"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def preprocess(text):
    return re.findall(r'\b\w+\b', text.lower())

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def create_bm25_index(chunks):
    tokenized_corpus = [preprocess(chunk) for chunk in chunks]
    return BM25Okapi(tokenized_corpus)

def retrieve_top_chunks(query, chunks, bm25, top_k=3):
    tokenized_query = preprocess(query)
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [chunks[i] for i in top_indices]

def process_document(file_path):
    print(f"🔄 Обработка файла: {file_path}")
    text = extract_text(file_path)
    chunks = split_text_into_chunks(text)
    metadata = {"source": file_path}
    save_chunks(chunks, metadata)
    print(f"✅ Сохранено {len(chunks)} чанков")

def ask_question(question: str, model: str = "qwen2:0.5b-instruct"):
    chunks, metadata = load_chunks()
    if not chunks:
        return "Не загружены документы. Загрузите файл."

    bm25 = create_bm25_index(chunks)
    relevant_chunks = retrieve_top_chunks(question, chunks, bm25, top_k=3)

    context = "\n\n".join(relevant_chunks)

    prompt = f"""
Ты — помощник, отвечающий на вопросы на основе предоставленного контекста.
Если ответа нет в контексте — скажи, что не знаешь.

Контекст:
{context}

Вопрос: {question}
Ответ:
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    # 🔥 ДОБАВЬ ЭТО:
    print(f"📡 Отправляю запрос в Ollama на: {OLLAMA_API}")
    print(f"📄 Параметры: {payload}")

    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Ошибка при генерации.")
    except Exception as e:
        print(f"❌ Ошибка при обращении к Ollama: {e}")
        return f"Ошибка Ollama: {str(e)}"