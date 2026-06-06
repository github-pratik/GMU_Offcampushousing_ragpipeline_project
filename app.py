"""Milestone 5 — Streamlit web UI for The Unofficial Guide.

Run locally:
    streamlit run app.py

On Streamlit Community Cloud, set GROQ_API_KEY in the app's Secrets. The vector
index is built on first load (cached), so the deploy needs only documents/.
"""
import os

import streamlit as st
import chromadb

from index import build_index, CHROMA_DIR, COLLECTION_NAME
from rag import Retriever, generate_answer

st.set_page_config(page_title="The Unofficial Guide — GMU Housing", page_icon="🏠", layout="centered")

# Pick up the Groq key from Streamlit secrets when deployed (local uses .env).
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

EXAMPLES = [
    "Which complexes near GMU have pest problems?",
    "How much does extra parking cost at The Point at Fairfax?",
    "What is the average rent near George Mason University?",
    "Which apartments have a free CUE bus to GMU?",
    "What do residents say about noise at eaves Fairfax City?",
]


@st.cache_resource(show_spinner="Loading the guide (embedding model + index)...")
def get_retriever():
    """Build the index on first run (fresh deploy), then load the retriever once."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.get_collection(COLLECTION_NAME)
    except Exception:
        build_index()
    return Retriever()


with st.sidebar:
    st.header("About")
    st.write(
        "A RAG system over real tenant reviews and listings for **off-campus housing "
        "near George Mason University** (Fairfax, VA). Answers are grounded only in the "
        "retrieved sources and cite where they came from."
    )
    st.markdown(
        "**Stack:** sentence-transformers (all-MiniLM-L6-v2) → ChromaDB + BM25 "
        "(hybrid, RRF) → Groq llama-3.3-70b"
    )
    st.caption("Tenant-review content was compiled from public review sites; see each source link.")

st.title("🏠 The Unofficial Guide")
st.caption("Ask about off-campus housing near GMU — grounded, cited answers from real reviews.")

retriever = get_retriever()

query = st.text_input("Your question", placeholder=EXAMPLES[0])
st.caption("Try: " + "  ·  ".join(f"_{q}_" for q in EXAMPLES[1:3]))

col1, col2 = st.columns([3, 2])
with col1:
    ask = st.button("Ask", type="primary", use_container_width=True)
with col2:
    semantic_only = st.toggle("Semantic-only (no BM25)", value=False)

if ask and query.strip():
    with st.spinner("Searching reviews..."):
        hits = retriever.retrieve(query, k=5, semantic_only=semantic_only)

    try:
        with st.spinner("Generating a grounded answer..."):
            ans = generate_answer(query, hits)
        st.markdown("### Answer")
        st.write(ans)
    except RuntimeError as e:
        st.error(str(e))

    st.markdown("### Sources")
    for i, c in enumerate(hits, 1):
        with st.expander(f"[{i}] {c['title']} — {c['doc_id']}"):
            st.write(c["text"])
            if c.get("source"):
                st.caption(f"Source: {c['source']}")
elif ask:
    st.warning("Type a question first.")
