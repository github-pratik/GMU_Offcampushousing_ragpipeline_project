"""Milestone 6 — Evaluation harness for The Unofficial Guide.

Runs the 5 planning.md test questions (plus the planned failure case) through the
full pipeline and prints a Markdown report (also written to evaluation_results.md):
expected answer, retrieved sources, and the grounded answer. Also compares hybrid
vs semantic-only retrieval for the stretch-goal write-up.

    python evaluate.py
"""
import os

from dotenv import load_dotenv

from index import BASE_DIR
from rag import Retriever, generate_answer

load_dotenv(os.path.join(BASE_DIR, ".env"))

EVAL_QUESTIONS = [
    ("Which apartment complexes near GMU have reported pest problems (cockroaches, mice, or bedbugs)?",
     "Oakton Park (German cockroaches) and Layton Hall (cockroaches, mice, bedbugs)."),
    ("How much does extra or reserved parking cost at The Point at Fairfax?",
     "About $100/month for an additional space and $125/month for reserved parking."),
    ("What is the average rent for an apartment near George Mason University?",
     "About $2,680 per month."),
    ("Which student apartments advertise free CUE bus rides to GMU?",
     "The Flats on University and The Main on University."),
    ("What do residents say about noise at eaves Fairfax City?",
     "Neighbors are loud past midnight ('beds shake'); management only enforces quiet hours (10pm-8am)."),
]

FAILURE_CASE = (
    "Is Oakton Park a good place to live?",
    "Sources deliberately conflict (high aggregate rating vs. reviews citing roaches, "
    "bad parking, and noise) -- expect a one-sided or over-confident answer.",
)


def _titles(hits):
    """Unique source titles, preserving rank order."""
    return ", ".join(dict.fromkeys(c["title"] for c in hits))


def run():
    retriever = Retriever()
    key = os.environ.get("GROQ_API_KEY", "").strip()
    have_key = bool(key) and key != "your_key_here"

    rows = [(f"Q{i}", q, a) for i, (q, a) in enumerate(EVAL_QUESTIONS, 1)]
    rows.append(("Failure case", FAILURE_CASE[0], FAILURE_CASE[1]))

    lines = ["# Evaluation Results — The Unofficial Guide\n"]
    for tag, question, expected in rows:
        hits = retriever.retrieve(question, k=5)
        if have_key:
            try:
                ans = generate_answer(question, hits)
            except Exception as e:  # noqa: BLE001
                ans = f"[generation error: {e}]"
        else:
            ans = "[generation skipped: GROQ_API_KEY not set]"
        lines += [
            f"## {tag}: {question}",
            f"- **Expected:** {expected}",
            f"- **Retrieved (hybrid, top-5):** {_titles(hits)}",
            f"- **System answer:** {ans}",
            "",
        ]

    # Hybrid vs. semantic-only retrieval comparison (stretch-goal write-up).
    lines += ["## Hybrid vs. semantic-only retrieval (top-5 source titles)",
              "| Question | Hybrid (semantic + BM25) | Semantic-only |",
              "|---|---|---|"]
    for tag, question, _ in rows:
        hybrid = _titles(retriever.retrieve(question, k=5))
        semantic = _titles(retriever.retrieve(question, k=5, semantic_only=True))
        lines.append(f"| {tag} | {hybrid} | {semantic} |")
    lines.append("")

    report = "\n".join(lines)
    print(report)
    out_path = os.path.join(BASE_DIR, "evaluation_results.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"(Written to {out_path})")


if __name__ == "__main__":
    run()
