# backend/vector_store.py

import json
import os

VECTOR_STORE_PATH = "../documents/chunks.json"


def save_chunks(chunks, metadata):
    """Сохраняет список чанков и метаданных в JSON"""
    data = {
        "chunks": chunks,
        "metadata": metadata
    }
    os.makedirs(os.path.dirname(VECTOR_STORE_PATH), exist_ok=True)
    with open(VECTOR_STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_chunks():
    """Загружает чанки и метаданные из JSON"""
    if not os.path.exists(VECTOR_STORE_PATH):
        return [], []
    with open(VECTOR_STORE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["chunks"], data["metadata"]