# backend/rag.py

import re
import json
import numpy as np
from utils import extract_text
from vector_store import save_chunks, load_chunks
import requests

OLLAMA_API = "http://localhost:11434/api/generate"
EMBEDDING_MODEL = "nomic-embed-text"
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


def get_embedding(text, model=EMBEDDING_MODEL):
    """Получает эмбеддинг текста через Ollama"""
    try:
        response = requests.post(
            f"http://localhost:11434/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=10
        )
        response.raise_for_status()
        embedding = response.json().get("embedding")
        if not embedding:
            raise ValueError("Empty embedding")
        return embedding
    except Exception as e:
        print(f"❌ Ошибка при генерации эмбеддинга: {e}")
        return [0.0] * 768  # fallback размерность nomic-embed-text


def cosine_similarity(a, b):
    """Вычисляет косинусное сходство между двумя векторами"""
    a = np.array(a)
    b = np.array(b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def retrieve_top_chunks(query, chunks, embeddings, top_k=3):
    """Находит top-k наиболее релевантных чанков по эмбеддингам"""
    query_embedding = get_embedding(query)

    similarities = []
    for i, emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append((i, sim))

    # Сортируем по схожести (по убыванию)
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, _ in similarities[:top_k]]
    return [chunks[i] for i in top_indices]


def process_document(file_path):
    print(f"🔄 Обработка файла: {file_path}")
    text = extract_text(file_path)
    chunks = split_text_into_chunks(text)
    metadata = [{"source": file_path} for _ in chunks]

    print("🧠 Генерирую эмбеддинги для чанков...")
    embeddings = []
    for chunk in chunks:
        emb = get_embedding(chunk)
        embeddings.append(emb)

    save_chunks(chunks, metadata, embeddings)
    print(f"✅ Сохранено {len(chunks)} чанков с эмбеддингами")


def ask_question(question: str, model: str = "mistral:7b-instruct"):
    chunks, metadata, embeddings = load_chunks()
    if not chunks:
        return {"answer": "Не загружены документы. Загрузите файл.", "sources": []}

    print("🔍 Ищу релевантные фрагменты...")
    relevant_chunks = retrieve_top_chunks(question, chunks, embeddings, top_k=3)

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

    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        answer = result.get("response", "Ошибка при генерации.")
    except Exception as e:
        print(f"❌ Ошибка при обращении к Ollama: {e}")
        answer = f"Ошибка Ollama: {str(e)}"

    # Извлекаем уникальные источники
    sources = list(set([m["source"] for m in metadata]))

    return {
        "answer": answer,
        "sources": sources
    }