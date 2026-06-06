"""Milestone 3 — Document ingestion for The Unofficial Guide.

Loads the raw .txt files in documents/, parses the SOURCE/TYPE/COLLECTED/TOPIC
header into metadata, separates the body, and lightly cleans it. The cleaned
documents are the input to chunk.py.

Run directly to inspect the corpus:
    python ingest.py
"""
import os
import re
import glob
import html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DOCS_DIR = os.path.join(BASE_DIR, "documents")

HEADER_KEYS = ("SOURCE", "TYPE", "COLLECTED", "TOPIC")


def _derive_title(path):
    """Human-readable label from a filename: review_oakton_park.txt -> 'Oakton Park'."""
    base = os.path.splitext(os.path.basename(path))[0]
    for prefix in ("review_", "factual_", "guide_"):
        if base.startswith(prefix):
            base = base[len(prefix):]
            break
    return base.replace("_", " ").title()


def clean_text(text):
    """Light cleaning: decode HTML entities, strip tags, normalize whitespace."""
    text = html.unescape(text)              # &amp; -> &, &nbsp; -> space, etc.
    text = re.sub(r"<[^>]+>", "", text)     # strip any stray HTML tags
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse big blank gaps
    return text.strip()


def parse_document(path):
    """Parse one .txt file into {doc_id, title, source, type, topic, text}."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    meta = {key.lower(): "" for key in HEADER_KEYS}
    header, sep, body = raw.partition("\n---\n")
    if not sep:                             # no header delimiter; treat whole file as body
        header, body = "", raw

    for line in header.splitlines():
        m = re.match(r"^\s*(SOURCE|TYPE|COLLECTED|TOPIC):\s*(.*)$", line)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()

    return {
        "doc_id": os.path.basename(path),
        "title": _derive_title(path),
        "source": meta["source"],
        "type": meta["type"],
        "topic": meta["topic"],
        "text": clean_text(body),
    }


def load_documents(docs_dir=DEFAULT_DOCS_DIR):
    """Load and parse every .txt file in docs_dir (sorted by filename)."""
    paths = sorted(glob.glob(os.path.join(docs_dir, "*.txt")))
    return [parse_document(p) for p in paths]


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {DEFAULT_DOCS_DIR}\n")
    for d in docs:
        words = len(d["text"].split())
        print(f"  {d['doc_id']:42} {d['title']:26} {words:4d} words  [{d['type']}]")

    total_words = sum(len(d["text"].split()) for d in docs)
    print(f"\nTotal body words: {total_words}")

    # Print one cleaned document in full so we can read it (Milestone 3 step).
    sample = docs[0]
    print("\n" + "=" * 70)
    print(f"SAMPLE CLEANED DOCUMENT: {sample['doc_id']}")
    print(f"source: {sample['source']}")
    print("=" * 70)
    print(sample["text"])
