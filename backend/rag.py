# backend/rag.py

import re
from rankbm25 import BM25Okapi
from utils import extract_text
from vector_store import save_chunks, load_chunks

OLLAMA_API = "http://host.docker.internal:11434/api/generate"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def preprocess(text):
    """Простая токенизация для BM25"""
    return re.findall(r'\b\w+\b', text.lower())


def split_text_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Разбивает текст на чанки с перекрытием"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def create_bm25_index(chunks):
    """Создаёт BM25 индекс для поиска"""
    tokenized_corpus = [preprocess(chunk) for chunk in chunks]
    return BM25Okapi(tokenized_corpus)


def retrieve_top_chunks(query, chunks, bm25, top_k=3):
    """Возвращает top-k наиболее релевантных чанков"""
    tokenized_query = preprocess(query)
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [chunks[i] for i in top_indices]


def process_document(file_path):
    """Обрабатывает загруженный файл: парсит → разбивает → сохраняет"""
    print(f"🔄 Обработка файла: {file_path}")
    text = extract_text(file_path)
    chunks = split_text_into_chunks(text)
    metadata = {"source": file_path}

    save_chunks(chunks, metadata)
    print(f"✅ Сохранено {len(chunks)} чанков")


def ask_question(question: str, model: str = "mistral:7b-instruct"):
    """Генерирует ответ на вопрос, используя релевантные чанки"""
    chunks, metadata = load_chunks()
    if not chunks:
        return "Не загружены документы. Загрузите файл."

    # Создаем индекс BM25 (можно кэшировать, но для малого числа документов — быстро)
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

    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Ошибка при генерации.")
    except Exception as e:
        return f"Ошибка Ollama: {str(e)}"