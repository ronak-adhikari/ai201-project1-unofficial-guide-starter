import os
import re
from sentence_transformers import SentenceTransformer
import chromadb

# ── 1. INGESTION ──────────────────────────────────────────────────────────────

def load_documents(docs_folder="documents"):
    """Load all .txt files from the documents folder"""
    documents = []
    for filename in os.listdir(docs_folder):
        if filename.endswith(".txt") and filename != ".gitkeep":
            filepath = os.path.join(docs_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({
                "filename": filename,
                "text": text
            })
            print(f"Loaded: {filename} ({len(text)} characters)")
    return documents


def clean_text(text):
    """Clean raw review text and remove the header block"""
    # Remove the header metadata block (everything before the first "Review")
    if "Review 1:" in text:
        text = text[text.index("Review 1:"):]
    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def chunk_text(text, chunk_size=500, overlap=75):
    """
    Split text at review boundaries first, then by size if needed.
    This keeps each review as its own chunk where possible.
    """
    # Split on "Review N:" markers
    review_pattern = re.split(r'(Review \d+:)', text)
    
    # Reassemble into individual review chunks
    raw_chunks = []
    i = 0
    while i < len(review_pattern):
        part = review_pattern[i].strip()
        if re.match(r'Review \d+:', part):
            # Combine the "Review N:" label with its content
            label = part
            content = review_pattern[i+1].strip() if i+1 < len(review_pattern) else ""
            combined = f"{label}\n{content}".strip()
            if len(combined) > 30:
                raw_chunks.append(combined)
            i += 2
        else:
            if part and len(part) > 30:
                raw_chunks.append(part)
            i += 1

    # If any chunk is too large, split it further
    final_chunks = []
    for chunk in raw_chunks:
        if len(chunk) <= chunk_size:
            final_chunks.append(chunk)
        else:
            # Fall back to character splitting with word boundary respect
            start = 0
            while start < len(chunk):
                end = start + chunk_size
                if end < len(chunk):
                    while end > start and chunk[end] != ' ':
                        end -= 1
                    if end == start:
                        end = start + chunk_size
                piece = chunk[start:end].strip()
                if len(piece) > 30:
                    final_chunks.append(piece)
                start += chunk_size - overlap

    return final_chunks


# ── 4. EMBEDDING + VECTOR STORE ───────────────────────────────────────────────

def build_vector_store(documents, collection_name="professor_reviews"):
    """Embed all chunks and store in ChromaDB"""

    # Load embedding model (runs locally, no API key needed)
    print("\nLoading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model loaded.")

    # Set up ChromaDB (stores locally in ./chroma_db folder)
    client = chromadb.PersistentClient(path="./chroma_db")

    # Delete existing collection if it exists (clean rebuild)
    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        pass

    collection = client.create_collection(collection_name)
    print(f"Created collection: {collection_name}")

    total_chunks = 0

    for doc in documents:
        filename = doc["filename"]
        text = clean_text(doc["text"])
        chunks = chunk_text(text, chunk_size=500, overlap=75)

        # Extract professor name from file header
        prof_name = ""
        for line in doc["text"].split("\n"):
            if line.startswith("Professor:"):
                prof_name = line.replace("Professor:", "").strip()
                break

        print(f"\nProcessing {filename}: {len(chunks)} chunks | Professor: {prof_name}")

        # Prepend professor name to each chunk before embedding
        enriched_chunks = [f"[{prof_name}] {chunk}" for chunk in chunks]

        # Embed all enriched chunks at once
        embeddings = model.encode(enriched_chunks).tolist()

        # Store each chunk with its embedding and metadata
        for i, (enriched_chunk, embedding) in enumerate(zip(enriched_chunks, embeddings)):
            chunk_id = f"{filename}_chunk_{i}"
            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[enriched_chunk],
                metadatas=[{
                    "source": filename,
                    "chunk_index": i,
                    "professor": prof_name
                }]
            )
            total_chunks += 1

    print(f"\nTotal chunks stored: {total_chunks}")
    return collection, model


# ── 5. RETRIEVAL ──────────────────────────────────────────────────────────────

def retrieve(query, collection, model, top_k=5):
    """
    Given a query string, return the top_k most relevant chunks
    with their source metadata and distance scores.
    """
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "chunk": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": round(results["distances"][0][i], 4)
        })

    return retrieved


# ── 6. TEST RETRIEVAL ─────────────────────────────────────────────────────────

def test_retrieval(collection, model):
    """Run 3 test queries and print results"""

    test_queries = [
        "What do students say about Professor Nachawati's organization?",
        "What do students say about Professor Sharifian's lectures and exams?",
        "What is Professor Prombutr's overall class structure like?"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print('='*60)

        results = retrieve(query, collection, model, top_k=5)

        for j, result in enumerate(results):
            print(f"\nResult {j+1} | Source: {result['source']} | Distance: {result['distance']}")
            print(f"Chunk: {result['chunk'][:200]}...")


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== LOADING DOCUMENTS ===")
    documents = load_documents("documents")
    print(f"\nLoaded {len(documents)} documents")

    print("\n=== BUILDING VECTOR STORE ===")
    collection, model = build_vector_store(documents)

    print("\n=== TESTING RETRIEVAL ===")
    test_retrieval(collection, model)

    print("\n✅ Pipeline complete!")