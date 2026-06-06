"""Milestones 4-5 — Hybrid retrieval (M4) and grounded generation (M5).

Retrieval combines semantic search (ChromaDB + all-MiniLM-L6-v2) with BM25
keyword search, fused via Reciprocal Rank Fusion. Hybrid helps here because
housing questions are full of proper nouns (complex names, "mold", "CUE bus")
that BM25 matches exactly while embeddings catch paraphrases.

Generation sends the retrieved chunks to Groq (llama-3.3-70b) with a grounding
system prompt: answer only from the sources, cite them, and decline when the
answer isn't present.

    python rag.py "which complexes have cockroaches?"            # retrieval only
    python rag.py "extra parking cost at the point" --answer     # grounded answer
    python rag.py "is the housing lottery random?" --answer      # should decline
"""
import os
import re
import argparse

import chromadb
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

from ingest import load_documents
from chunk import chunk_documents
from index import BASE_DIR, CHROMA_DIR, COLLECTION_NAME, get_model, embed_text

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are The Unofficial Guide, a question-answering assistant for George Mason "
    "University off-campus housing. Answer ONLY using the numbered sources provided "
    "in the user message. Cite the sources you use with bracketed numbers like [1] "
    "or [2]. If the sources do not contain the answer, say you don't have that "
    "information in your sources -- do not use outside knowledge and do not guess. "
    "Be concise and specific, and prefer concrete details (names, prices, specifics) "
    "from the sources."
)


def _tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def _rrf_fuse(rank_lists, k, rrf_k=60):
    """Reciprocal Rank Fusion of several ranked id lists -> top-k ids."""
    scores = {}
    for ids in rank_lists:
        for rank, _id in enumerate(ids):
            scores[_id] = scores.get(_id, 0.0) + 1.0 / (rrf_k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)[:k]


class Retriever:
    """Loads the vector store + BM25 index and answers retrieval queries."""

    def __init__(self):
        self.model = get_model()
        self.collection = chromadb.PersistentClient(path=CHROMA_DIR).get_collection(COLLECTION_NAME)
        self.chunks = chunk_documents(load_documents())
        self.by_id = {c["id"]: c for c in self.chunks}
        self.ids = [c["id"] for c in self.chunks]
        # BM25 over title-prefixed text so complex names are always keyword-matchable.
        self.bm25 = BM25Okapi([_tokenize(embed_text(c)) for c in self.chunks])

    def _semantic(self, query, n):
        emb = self.model.encode([query], normalize_embeddings=True).tolist()
        res = self.collection.query(query_embeddings=emb, n_results=n)
        return res["ids"][0]

    def _bm25(self, query, n):
        scores = self.bm25.get_scores(_tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.ids[i] for i in order[:n]]

    def retrieve(self, query, k=5, semantic_only=False, pool=20):
        """Return the top-k chunk dicts for a query."""
        sem = self._semantic(query, pool)
        if semantic_only:
            top_ids = sem[:k]
        else:
            top_ids = _rrf_fuse([sem, self._bm25(query, pool)], k)
        return [self.by_id[i] for i in top_ids]


def format_context(hits):
    """Number the retrieved chunks so the model can cite them."""
    return "\n\n".join(f"[{i}] ({c['title']}) {c['text']}" for i, c in enumerate(hits, 1))


def generate_answer(query, hits, model=GROQ_MODEL, temperature=0.2):
    """Call Groq with the grounded prompt. Raises RuntimeError if no API key."""
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add your free key to the .env file "
            "(get one at https://console.groq.com)."
        )
    from groq import Groq

    client = Groq(api_key=api_key)
    user_msg = f"Sources:\n{format_context(hits)}\n\nQuestion: {query}"
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def answer(query, k=5, semantic_only=False, retriever=None):
    """Retrieve + generate. Returns {'answer': str, 'sources': [chunk, ...]}."""
    retriever = retriever or Retriever()
    hits = retriever.retrieve(query, k=k, semantic_only=semantic_only)
    return {"answer": generate_answer(query, hits), "sources": hits}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Retrieve (and optionally answer) over the GMU housing corpus")
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--semantic-only", action="store_true")
    ap.add_argument("--answer", action="store_true", help="generate a grounded answer (needs GROQ_API_KEY)")
    args = ap.parse_args()

    retriever = Retriever()
    hits = retriever.retrieve(args.query, k=args.k, semantic_only=args.semantic_only)
    mode = "semantic-only" if args.semantic_only else "hybrid (semantic + BM25 via RRF)"

    if args.answer:
        print(f"Q: {args.query}\n")
        print(generate_answer(args.query, hits))
        print("\nSources:")
        for i, c in enumerate(hits, 1):
            print(f"  [{i}] {c['title']} ({c['doc_id']} #{c['chunk_index']})")
    else:
        print(f"Query: {args.query!r}   mode: {mode}   top-{args.k}\n")
        for i, c in enumerate(hits, 1):
            print(f"{i}. [{c['title']}]  ({c['doc_id']} #{c['chunk_index']})")
            print(f"   {c['text']}\n")
