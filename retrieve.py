"""
Milestone 4: Embedding + vector store + retrieval.

The Unofficial Guide -- unofficial student knowledge about Furman dining.

Pipeline stage:  Chunking -> [ Embedding + Vector Store -> Retrieval ] -> Generation

What this script does:
  1. Loads the chunks produced in Milestone 3 (output/chunks.json).
  2. Embeds each chunk with sentence-transformers/all-MiniLM-L6-v2.
  3. Stores the chunks + embeddings in a persistent ChromaDB collection,
     keeping source filename and chunk number (plus title/url) as metadata.
  4. Provides retrieve(query) -> the top-5 most relevant chunks.
  5. Prints each result's text, source filename, chunk number, and distance.
  6. Runs the 3 evaluation questions from planning.md.

Run it with:   python retrieve.py

The ChromaDB store persists in chroma_db/ so Milestone 5 can reuse it without
re-embedding. Re-run with `python retrieve.py --rebuild` to force a fresh index
(do this whenever output/chunks.json changes).
"""

import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# Print UTF-8 so accented names (Bon Appétit, café) show correctly on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- Configuration (matches planning.md Retrieval Approach) --------------
CHUNKS_FILE = Path("output/chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "furman_dining"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5

# Evaluation questions (from the planning.md Evaluation Plan).
TEST_QUESTIONS = [
    "What do students say about the best place to eat when they are in a hurry?",
    "What dining option seems most associated with wait time or crowding complaints?",
    "What vegetarian, vegan, or gluten-free options are mentioned?",
]


# =========================================================================
# Build the vector store
# =========================================================================
def load_chunks() -> list[dict]:
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")
    return chunks


def get_collection(model: SentenceTransformer, rebuild: bool = False):
    """
    Return a ChromaDB collection populated with our embedded chunks.

    Uses cosine distance (the natural metric for these sentence embeddings),
    so scores range 0 (identical meaning) to 2 (opposite). Lower = more similar.
    Re-embeds only when the store is empty/stale, or when rebuild=True.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    if rebuild:
        print("--rebuild: deleting any existing store and re-embedding from scratch.")
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    chunks = load_chunks()

    # Skip re-embedding if the store already matches the chunk file.
    if collection.count() == len(chunks) and not rebuild:
        print(f"Vector store already built: {collection.count()} chunks (reusing).")
        return collection

    # Fresh build: clear anything stale, then embed + add everything.
    if collection.count() > 0:
        client.delete_collection(COLLECTION_NAME)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    print(f"Embedding {len(chunks)} chunks with {MODEL_NAME} ...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    collection.add(
        ids=[f"{c['source']}::chunk{c['chunk_number']}" for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": c["source"],            # source filename (required)
                "chunk_number": c["chunk_number"],  # chunk number (required)
                "source_title": c["source_title"],
                "url": c["url"],
            }
            for c in chunks
        ],
    )
    print(f"Stored {collection.count()} chunks in ChromaDB ('{COLLECTION_NAME}').")
    return collection


# =========================================================================
# Retrieval
# =========================================================================
def retrieve(query: str, model: SentenceTransformer, collection, k: int = TOP_K) -> list[dict]:
    """Embed the query and return the top-k most similar chunks."""
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    # Flatten Chroma's nested (per-query) result lists into a simple list.
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits


def print_results(query: str, hits: list[dict]) -> None:
    # --- How to read the distance score -----------------------------------
    # We use COSINE distance (set on the collection), so:
    #   distance = 0.0  -> identical meaning to the query
    #   distance ~ 1.0  -> unrelated
    #   distance = 2.0  -> opposite meaning
    # LOWER is better. For this small model (all-MiniLM-L6-v2) on paraphrased
    # questions, ~0.3-0.45 is a strong match, ~0.45-0.6 is loosely related,
    # and > ~0.7 usually means the corpus doesn't really answer the query.
    # A big jump in distance down the list marks where results stop being relevant.
    print("\n" + "=" * 78)
    print(f"QUERY: {query}")
    print("=" * 78)
    for rank, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        print(f"\n[{rank}] distance={hit['distance']:.4f}   (lower = more relevant)")
        print(f"    source filename : {meta['source']}")
        print(f"    chunk number    : {meta['chunk_number']}")
        print(f"    metadata        : {meta}")          # full stored metadata
        print(f"    text:\n{hit['text']}")              # full chunk text, not truncated


# =========================================================================
# Main
# =========================================================================
def main() -> None:
    rebuild = "--rebuild" in sys.argv

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    collection = get_collection(model, rebuild=rebuild)

    for question in TEST_QUESTIONS:
        hits = retrieve(question, model, collection)
        print_results(question, hits)

    print("\n" + "=" * 78)
    print("Done. Lower distance = more semantically similar to the query.")
    print("=" * 78)


if __name__ == "__main__":
    main()
