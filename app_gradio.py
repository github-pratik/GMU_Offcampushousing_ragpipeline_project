"""Optional Gradio UI for The Unofficial Guide (alternative to the Streamlit app.py).

Same backend (rag.py) — handy if you'd rather deploy to Hugging Face Spaces.
Run:  python app_gradio.py        # serves on http://localhost:7860
"""
import os

import chromadb
import gradio as gr
from dotenv import load_dotenv

from index import BASE_DIR, build_index, CHROMA_DIR, COLLECTION_NAME
from rag import Retriever, generate_answer

load_dotenv(os.path.join(BASE_DIR, ".env"))

# Build the vector index on first run (fresh deploy), then load the retriever once.
try:
    chromadb.PersistentClient(path=CHROMA_DIR).get_collection(COLLECTION_NAME)
except Exception:
    build_index()
retriever = Retriever()


def handle_query(question):
    if not question or not question.strip():
        return "Type a question first.", ""
    hits = retriever.retrieve(question, k=5)
    try:
        answer_text = generate_answer(question, hits)
    except RuntimeError as e:                       # no GROQ_API_KEY
        answer_text = f"⚠️ {e}"
    # Our sources are chunk dicts, so format them into readable lines.
    sources = "\n".join(
        f"[{i}] {c['title']} — {c['doc_id']}\n    {c['source']}".rstrip()
        for i, c in enumerate(hits, 1)
    )
    return answer_text, sources


with gr.Blocks(title="The Unofficial Guide — GMU Housing") as demo:
    gr.Markdown(
        "# 🏠 The Unofficial Guide\n"
        "Ask about off-campus housing near George Mason University — "
        "grounded, cited answers from real tenant reviews."
    )
    inp = gr.Textbox(label="Your question",
                     placeholder="e.g. Which complexes near GMU have pest problems?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=6)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
