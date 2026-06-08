"""
Milestone 5: Grounded generation + a simple query interface.

The Unofficial Guide -- unofficial student knowledge about Furman dining.

Pipeline stage:  ... Retrieval -> [ Generation ] -> Grounded answer with sources

What this script does:
  1. Reuses the Milestone 4 retrieval code (retrieve.py) to fetch the top-5
     chunks for a query from ChromaDB.
  2. Sends those chunks to Groq's llama-3.3-70b-versatile with a prompt that
     tells the model to answer ONLY from the provided sources.
  3. If the sources are insufficient, the model returns a fixed refusal line.
  4. Prints the answer plus a Sources list built from the retrieved METADATA
     (source filename + chunk number + title + url) -- so attribution comes
     from our data, never from text the model made up.

Run it:
  python generate.py            # runs the test questions (in-scope + out-of-scope)
  python generate.py --chat     # interactive: type your own questions
  python generate.py --show-context   # also print the retrieved chunks (grounding check)

Requires GROQ_API_KEY in a .env file.
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# Reuse the exact Milestone 4 retrieval pipeline.
from retrieve import get_collection, retrieve, MODEL_NAME, TOP_K

# Print UTF-8 so accented names (Bon Appétit, café) show correctly on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- Configuration -------------------------------------------------------
LLM_MODEL = "llama-3.3-70b-versatile"
# Exact line the model must use when the sources can't answer the question.
REFUSAL = "I don't have enough information in the provided sources to answer that."

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about Furman University "
    "dining using ONLY the numbered sources given in the user's message.\n"
    "Rules:\n"
    "1. Use only information found in the provided sources. Do not use any outside "
    "knowledge or assumptions.\n"
    f'2. If the sources do not contain enough information to answer, reply with '
    f'EXACTLY this sentence and nothing else: "{REFUSAL}"\n'
    "3. When you state a fact, cite the source it came from using its bracket label, "
    "for example [Source 2].\n"
    "4. Never invent source names, filenames, or URLs. Only refer to the sources given.\n"
    "5. Keep the answer concise and grounded in the sources."
)

# In-scope + out-of-scope test questions (req. 8).
TEST_QUESTIONS = [
    "What do students say about the best place to eat when they are in a hurry?",
    "What vegetarian, vegan, or gluten-free options are mentioned?",
    "What do students say about wait times or crowding in the dining hall?",
    "How do I register for fall semester classes at Furman?",  # out of scope (not dining)
]


def build_context(hits: list[dict]) -> str:
    """Turn retrieved chunks into a numbered, labeled context block for the LLM."""
    blocks = []
    for i, hit in enumerate(hits, start=1):
        m = hit["metadata"]
        blocks.append(
            f"[Source {i}] file={m['source']}, chunk={m['chunk_number']}, "
            f"title={m['source_title']}\n{hit['text']}"
        )
    return "\n\n".join(blocks)


def format_sources(hits: list[dict]) -> str:
    """Build the Sources list straight from metadata (NOT from the model)."""
    lines = []
    for i, hit in enumerate(hits, start=1):
        m = hit["metadata"]
        lines.append(
            f"  [Source {i}] {m['source']} (chunk {m['chunk_number']}) "
            f"- {m['source_title']} - {m['url']} (distance {hit['distance']:.3f})"
        )
    return "\n".join(lines)


def answer_query(query: str, client: Groq, model: SentenceTransformer, collection) -> dict:
    """Retrieve -> prompt the LLM -> return the grounded answer and its sources."""
    hits = retrieve(query, model, collection, k=TOP_K)
    context = build_context(hits)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.2,  # low temperature keeps the answer close to the sources
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Sources:\n\n{context}\n\nQuestion: {query}"},
        ],
    )
    answer = response.choices[0].message.content.strip()
    return {"answer": answer, "hits": hits}


def print_answer(query: str, result: dict, show_context: bool = False) -> None:
    print("\n" + "=" * 78)
    print(f"QUESTION: {query}")
    print("=" * 78)

    if show_context:
        print("\n--- Retrieved chunks (the ONLY information the model may use) ---")
        for i, hit in enumerate(result["hits"], start=1):
            print(f"\n[Source {i}] {hit['metadata']['source']} "
                  f"(chunk {hit['metadata']['chunk_number']}, distance {hit['distance']:.3f})")
            print(hit["text"])
        print("\n--- End retrieved chunks ---")

    print("\n" + "-" * 78)
    print("ANSWER")
    print("-" * 78)
    print(result["answer"])

    print("\n" + "-" * 78)
    print("SOURCES CITED  (from retrieved metadata -- [Source N] above maps to these)")
    print("-" * 78)
    print(format_sources(result["hits"]))


def main() -> None:
    show_context = "--show-context" in sys.argv
    chat_mode = "--chat" in sys.argv

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        sys.exit("ERROR: GROQ_API_KEY not found. Add it to your .env file.")

    print(f"Loading embedding model: {MODEL_NAME}")
    embed_model = SentenceTransformer(MODEL_NAME)
    collection = get_collection(embed_model)  # reuses the persistent ChromaDB store
    client = Groq(api_key=api_key)
    print(f"Generation model: {LLM_MODEL}")

    if chat_mode:
        print("\nInteractive mode. Type a question (or 'quit' to exit).")
        while True:
            try:
                query = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if query.lower() in {"quit", "exit", ""}:
                break
            result = answer_query(query, client, embed_model, collection)
            print_answer(query, result, show_context)
    else:
        for question in TEST_QUESTIONS:
            result = answer_query(question, client, embed_model, collection)
            print_answer(question, result, show_context)

    print("\n" + "=" * 78)
    print("Grounding check: every fact in ANSWER should trace to a chunk above,")
    print("and the SOURCES list is built from metadata, not written by the model.")
    print("=" * 78)


if __name__ == "__main__":
    main()
