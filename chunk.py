"""Milestone 3 — Sentence-aware chunking for The Unofficial Guide.

Splits cleaned documents into ~300-character, sentence-aware chunks with 50
characters of overlap (see planning.md -> Chunking Strategy). Each chunk keeps
its source metadata so retrieval can cite the originating document.

Run directly to inspect chunks:
    python chunk.py
"""
import re

from ingest import load_documents

CHUNK_SIZE = 300      # characters; review text is short and opinion-based
OVERLAP = 50          # characters carried into the next chunk for context


def _split_units(text):
    """Break text into sentence-ish units, respecting line/bullet boundaries."""
    units = []
    for line in text.split("\n"):
        line = line.strip().lstrip("-•").strip()
        if not line:
            continue
        for part in re.split(r"(?<=[.!?])\s+", line):
            part = part.strip()
            if part:
                units.append(part)
    return units


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Pack sentence units into <= chunk_size chunks with character overlap."""
    units = _split_units(text)
    chunks = []
    current = ""
    for unit in units:
        if not current:
            current = unit
        elif len(current) + 1 + len(unit) <= chunk_size:
            current += " " + unit
        else:
            chunks.append(current)
            tail = current[-overlap:] if overlap and len(current) > overlap else ""
            if tail and " " in tail:                  # start overlap on a word boundary
                tail = tail[tail.find(" ") + 1:]
            current = (tail + " " + unit).strip() if tail else unit
    if current:
        chunks.append(current)
    return chunks


def chunk_documents(docs, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Chunk every document, carrying source metadata onto each chunk."""
    chunks = []
    for d in docs:
        for i, text in enumerate(chunk_text(d["text"], chunk_size, overlap)):
            chunks.append({
                "id": f"{d['doc_id']}::{i}",
                "text": text,
                "doc_id": d["doc_id"],
                "title": d["title"],
                "source": d["source"],
                "type": d["type"],
                "topic": d["topic"],
                "chunk_index": i,
            })
    return chunks


if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)

    print(f"{len(docs)} documents -> {len(chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={OVERLAP})")
    sizes = [len(c["text"]) for c in chunks]
    print(f"chunk length: min={min(sizes)} avg={sum(sizes) // len(sizes)} max={max(sizes)}")
    in_range = 50 <= len(chunks) <= 2000
    print(f"within 50-2000 range: {'YES' if in_range else 'NO -- adjust chunk size'}\n")

    # Print 5 representative chunks spread across the corpus, and read them.
    step = max(1, len(chunks) // 5)
    for c in chunks[::step][:5]:
        print("-" * 70)
        print(f"[{c['title']}] (chunk {c['chunk_index']}, {len(c['text'])} chars)")
        print(c["text"])
