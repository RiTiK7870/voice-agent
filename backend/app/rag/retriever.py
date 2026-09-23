from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DOCUMENTS_DIR = Path("documents")

MODEL_NAME = "all-MiniLM-L6-v2"

_model = SentenceTransformer(MODEL_NAME)

_chunks: List[Dict] = []
_index = None


def _load_documents():
    global _chunks

    if _chunks:
        return

    for path in DOCUMENTS_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        # Treat each document as a complete knowledge unit.
        # This keeps headings together with their policy content.
        _chunks.append(
            {
                "text": text,
                "source": path.name,
            }
        )


def _build_index():
    global _index

    _load_documents()

    if _index is not None:
        return

    texts = [item["text"] for item in _chunks]

    if not texts:
        return

    embeddings = _model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    dimension = embeddings.shape[1]

    _index = faiss.IndexFlatIP(dimension)
    _index.add(embeddings)


def retrieve(query: str, top_k: int = 3):
    if not query.strip():
        return []

    # Make sure documents and FAISS index are ready
    _build_index()

    if _index is None:
        return []

    query_embedding = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    scores, indices = _index.search(
        query_embedding,
        min(top_k, len(_chunks))
    )

    results = []

    SIMILARITY_THRESHOLD = 0.35

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        if float(score) < SIMILARITY_THRESHOLD:
            continue

        chunk = _chunks[idx]

        results.append(
            {
                "source": chunk["source"],
                "text": chunk["text"],
                "score": float(score),
            }
        )

    return results