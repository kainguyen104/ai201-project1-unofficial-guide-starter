"""
Milestone 3: Document ingestion and chunking pipeline.

The Unofficial Guide -- unofficial student knowledge about Furman dining.

What this script does (in order):
  1. Loads every .txt file from the data/ folder.
  2. Saves a copy of the RAW text (before cleaning) into output/raw/.
  3. Cleans each document: strips HTML, boilerplate (nav / cookie banners /
     footers / share buttons), and collapses extra whitespace -- while keeping
     the substantive dining content.
  4. Splits each cleaned document into 600-900 character chunks with
     100-150 characters of overlap (sentence-aware).
  5. Saves all chunks + metadata to output/chunks.json.
  6. Prints one cleaned document, 5 representative chunks, and the totals.

Run it with:   python ingest.py
"""

import html
import json
import re
import sys
from pathlib import Path

# Print UTF-8 so accented names (Bon Appétit, café) show correctly on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- Configuration (matches planning.md Chunking Strategy) ---------------
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
RAW_DIR = OUTPUT_DIR / "raw"
CHUNKS_FILE = OUTPUT_DIR / "chunks.json"

MIN_CHARS = 600       # don't end a chunk before this if more text remains
MAX_CHARS = 900       # never grow a chunk past this
OVERLAP_CHARS = 125   # carry ~this many chars from the end of one chunk to the next


# =========================================================================
# 1. Loading
# =========================================================================
def load_documents(data_dir: Path) -> list[dict]:
    """Read every .txt file in data_dir. Returns a list of doc dicts."""
    docs = []
    for path in sorted(data_dir.glob("*.txt")):
        raw_text = path.read_text(encoding="utf-8")
        docs.append({"filename": path.name, "raw_text": raw_text})
    return docs


def save_raw_copies(docs: list[dict], raw_dir: Path) -> None:
    """Preserve the raw text before any cleaning, so we can compare later."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for doc in docs:
        (raw_dir / doc["filename"]).write_text(doc["raw_text"], encoding="utf-8")


# =========================================================================
# 2. Header parsing -> source metadata
# =========================================================================
def split_header(raw_text: str) -> tuple[dict, str]:
    """
    Our source files start with a small metadata block:

        Source: ...
        URL: ...
        Date accessed: ...
        Description: ...

        <body text...>

    We pull Source + URL out as metadata and return the body separately so the
    header itself doesn't get chunked as if it were content.
    """
    parts = raw_text.split("\n\n", 1)
    header_block = parts[0]
    body = parts[1] if len(parts) > 1 else ""

    # If the first block doesn't actually look like a header, treat it all as body.
    if "Source:" not in header_block and "URL:" not in header_block:
        return {"source_title": "", "url": ""}, raw_text

    def grab(field: str) -> str:
        m = re.search(rf"^{field}:\s*(.+)$", header_block, flags=re.MULTILINE)
        return m.group(1).strip() if m else ""

    meta = {"source_title": grab("Source"), "url": grab("URL")}
    return meta, body


# =========================================================================
# 3. Cleaning
# =========================================================================
# Lines that are pure website boilerplate -- removed entirely.
BOILERPLATE_LINE = re.compile(
    r"^\s*("
    r"skip to (main )?content"
    r"|cookie(s)?( policy| settings| preferences)?\b.*"
    r"|we use cookies.*"
    r"|accept (all )?cookies"
    r"|privacy policy|terms of (use|service)"
    r"|all rights reserved.*"
    r"|©.*|copyright.*"
    r"|share (this|on).*|share button.*"
    r"|follow us.*|sign up.*|subscribe.*|newsletter.*"
    r"|back to top|menu\s*|toggle navigation|main navigation"
    r"|\d+ (posts|followers|following)"   # raw social-media counters
    r")\s*$",
    flags=re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """Remove HTML + boilerplate and normalize whitespace; keep real content."""
    # Decode HTML entities (&amp; -> &) then strip any HTML/XML tags.
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)

    # Drop boilerplate lines; keep everything substantive.
    kept_lines = [ln for ln in text.splitlines() if not BOILERPLATE_LINE.match(ln)]
    text = "\n".join(kept_lines)

    # Normalize whitespace: collapse runs of spaces/tabs, but keep paragraph breaks.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)   # 3+ blank lines -> one blank line
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)    # trim spaces around newlines

    return text.strip()


# =========================================================================
# 4. Chunking (sentence-aware, with overlap)
# =========================================================================
def split_sentences(text: str) -> list[str]:
    """Split into sentences, treating paragraph breaks as hard boundaries."""
    sentences = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.replace("\n", " ").strip()
        if not paragraph:
            continue
        # Break after . ! or ? followed by whitespace.
        for sent in re.split(r"(?<=[.!?])\s+", paragraph):
            sent = sent.strip()
            if not sent:
                continue
            # Safety net: hard-wrap a single sentence longer than MAX_CHARS.
            while len(sent) > MAX_CHARS:
                cut = sent.rfind(" ", 0, MAX_CHARS) or MAX_CHARS
                sentences.append(sent[:cut].strip())
                sent = sent[cut:].strip()
            sentences.append(sent)
    return sentences


def chunk_text(text: str) -> list[str]:
    """
    Group sentences into chunks of at most MAX_CHARS characters, with about
    OVERLAP_CHARS characters repeated between neighbouring chunks.

    A sliding window over the sentence list:
      * fill a chunk by adding whole sentences until the next one wouldn't fit,
      * then step the start index BACK by ~OVERLAP_CHARS worth of sentences so
        the following chunk re-includes the tail of this one (the overlap).
    Because we only add a sentence while it still fits, no chunk can exceed
    MAX_CHARS (single sentences are pre-capped to MAX_CHARS in split_sentences).
    """
    sentences = split_sentences(text)

    def fill(begin: int) -> int:
        """Return the end index of a window of whole sentences starting at begin."""
        end, length = begin, 0
        while end < len(sentences) and length + len(sentences[end]) + 1 <= MAX_CHARS:
            length += len(sentences[end]) + 1
            end += 1
        return max(end, begin + 1)             # always take at least one sentence

    chunks: list[str] = []
    n = len(sentences)
    start = 0
    prev_end = 0                               # first new (non-overlap) sentence index

    while start < n:
        end = fill(start)
        # If the overlap alone filled the window (a long sentence wouldn't fit
        # alongside it), drop the overlap so this chunk carries real new content.
        if end <= prev_end:
            start = prev_end
            end = fill(start)

        chunks.append(" ".join(sentences[start:end]).strip())
        if end >= n:
            break
        prev_end = end

        # Step back so the next chunk overlaps ~OVERLAP_CHARS with this one.
        back_len, k = 0, end
        while k > start and back_len < OVERLAP_CHARS:
            k -= 1
            back_len += len(sentences[k]) + 1
        start = max(k, start + 1)              # always make forward progress

    return chunks


# =========================================================================
# Pipeline
# =========================================================================
def build_chunks(docs: list[dict]) -> list[dict]:
    """Clean every doc and produce chunk records with source metadata."""
    all_chunks = []
    for doc in docs:
        meta, body = split_header(doc["raw_text"])
        cleaned = clean_text(body)
        doc["cleaned_text"] = cleaned

        for i, chunk in enumerate(chunk_text(cleaned), start=1):
            all_chunks.append({
                "source": doc["filename"],          # source filename (required)
                "chunk_number": i,                  # chunk number (required)
                "source_title": meta["source_title"],
                "url": meta["url"],
                "num_chars": len(chunk),
                "text": chunk,
            })
    return all_chunks


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1 + 2: load and preserve raw text.
    docs = load_documents(DATA_DIR)
    save_raw_copies(docs, RAW_DIR)

    # 3 + 4: clean and chunk.
    chunks = build_chunks(docs)

    # 5: save chunks with metadata.
    CHUNKS_FILE.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- Inspection output -------------------------------------------------
    sep = "=" * 70

    # Print one cleaned document so we can eyeball the cleaning step.
    sample_doc = docs[0]
    print(sep)
    print(f"CLEANED DOCUMENT SAMPLE: {sample_doc['filename']}")
    print(sep)
    print(sample_doc["cleaned_text"])
    print()

    # Print 5 representative chunks, evenly spaced so they come from varied sources.
    print(sep)
    print("5 REPRESENTATIVE CHUNKS")
    print(sep)
    if chunks:
        step = max(1, len(chunks) // 5)
        sample_idxs = [min(i * step, len(chunks) - 1) for i in range(5)]
        for idx in sorted(set(sample_idxs)):
            c = chunks[idx]
            print(f"\n--- {c['source']}  (chunk {c['chunk_number']}, {c['num_chars']} chars) ---")
            print(c["text"])

    # Totals + a quick chunk-quality summary.
    in_band = sum(1 for c in chunks if MIN_CHARS <= c["num_chars"] <= MAX_CHARS)
    too_big = sum(1 for c in chunks if c["num_chars"] > MAX_CHARS)
    sizes = [c["num_chars"] for c in chunks]
    print()
    print(sep)
    print(f"Total documents: {len(docs)}")
    print(f"Total chunks:    {len(chunks)}")
    print(f"Chunk size  -> min {min(sizes)}, max {max(sizes)}, avg {round(sum(sizes)/len(sizes))}")
    print(f"In target band ({MIN_CHARS}-{MAX_CHARS} chars): {in_band}/{len(chunks)}")
    print(f"Over the {MAX_CHARS}-char max: {too_big}  (should be 0)")
    print("(Chunks under the min are normal -- they are the short final piece of a document.)")
    print(f"Chunks saved to:   {CHUNKS_FILE}")
    print(f"Raw text saved to: {RAW_DIR}/")
    print(sep)


if __name__ == "__main__":
    main()
