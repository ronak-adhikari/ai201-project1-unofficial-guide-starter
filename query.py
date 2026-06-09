import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

# ── LOAD MODEL AND VECTOR STORE ───────────────────────────────────────────────

def load_retrieval_components():
    """Load the embedding model and ChromaDB collection"""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("professor_reviews")
    return model, collection

# ── RETRIEVAL ─────────────────────────────────────────────────────────────────

def retrieve(query, collection, model, top_k=5):
    """Return top_k most relevant chunks for a query"""
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
            "professor": results["metadatas"][0][i].get("professor", "Unknown"),
            "distance": round(results["distances"][0][i], 4)
        })

    return retrieved

# ── GENERATION ────────────────────────────────────────────────────────────────

def generate_answer(query, chunks):
    """Generate a grounded answer using Groq LLM"""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Format retrieved chunks as context
    context = ""
    for i, chunk in enumerate(chunks):
        context += f"\n[Source {i+1}: {chunk['source']}]\n{chunk['chunk']}\n"

    # System prompt enforces grounding strictly
    system_prompt = """You are an assistant that helps students at California State University Long Beach learn about professors based on Rate My Professors reviews.

STRICT RULES:
1. Answer ONLY using the information provided in the documents below. Do not use any outside knowledge.
2. If the documents do not contain enough information to answer the question, respond with: "I don't have enough information in the available reviews to answer that question."
3. Always cite which source document(s) your answer comes from using the format: (Source: filename)
4. Do not make up or infer information that is not explicitly stated in the documents.
5. Keep answers concise and focused on what students actually said in their reviews."""

    user_prompt = f"""Here are the retrieved student reviews:

{context}

Question: {query}

Answer the question using only the reviews above. Cite your sources."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content

# ── END-TO-END ASK FUNCTION ───────────────────────────────────────────────────

# Cache components so they load once
_model = None
_collection = None

def ask(query):
    """Full pipeline: retrieve chunks then generate grounded answer"""
    global _model, _collection

    # Load on first call, reuse after
    if _model is None or _collection is None:
        print("Loading retrieval components...")
        _model, _collection = load_retrieval_components()

    # Retrieve relevant chunks
    chunks = retrieve(query, _collection, _model, top_k=5)

    # Generate grounded answer
    answer = generate_answer(query, chunks)

    # Collect unique sources for attribution
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }


# ── TEST FROM COMMAND LINE ────────────────────────────────────────────────────

if __name__ == "__main__":
    test_queries = [
        "What do students say about Professor Nachawati's organization?",
        "What do students say about Professor Sharifian's lectures and exams?",
        "What is the weather like in Long Beach?"  # out-of-scope test
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print('='*60)
        result = ask(query)
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nSOURCES: {', '.join(result['sources'])}")