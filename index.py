"""Milestone 4 — Embed chunks and build the vector store.

Embeds every chunk with all-MiniLM-L6-v2 and stores it in a persistent ChromaDB
collection. Each chunk is embedded with its complex/title prefixed (e.g.
"Fairfax Square: ...") so chunks stay self-identifying even when a complaint
sentence doesn't repeat the complex name (planning.md -> Anticipated Challenges
#2). The raw chunk text is stored as the document for display and citation.

Run directly to (re)build the index:
    python index.py
"""
import os

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import load_documents
from chunk import chunk_documents

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "unofficial_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"

_model = None


def get_model():
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def embed_text(chunk):
    """Text we actually embed: title prefix + chunk, so each chunk self-identifies."""
    return f"{chunk['title']}: {chunk['text']}"


def build_index():
    """(Re)build the ChromaDB collection from the current documents/ corpus."""
    chunks = chunk_documents(load_documents())
    model = get_model()

    embeddings = model.encode(
        [embed_text(c) for c in chunks],
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)       # rebuild fresh each run
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[{
            "title": c["title"],
            "source": c["source"],
            "doc_id": c["doc_id"],
            "type": c["type"],
            "chunk_index": c["chunk_index"],
        } for c in chunks],
    )
    return collection


if __name__ == "__main__":
    print(f"Embedding model: {EMBED_MODEL}")
    collection = build_index()
    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}'")
    print(f"Vector store: {CHROMA_DIR}")
