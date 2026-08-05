from fastapi import FastAPI
from pydantic import BaseModel

from hybrid_search import load_all_chunks, multi_query_hybrid_search, rerank
from generate_answer import generate_answer

# --- FastAPI app banate hain ---
app = FastAPI(title="DevDocs-RAG API")

# --- Startup ke time par chunks ek baar load kar lete hain ---
# (har request pe baar-baar Qdrant se load karna slow hoga)
print("Loading all chunks from Qdrant (this happens once, at startup)...")
all_points = load_all_chunks()
print(f"Loaded {len(all_points)} chunks. API is ready.\n")


# --- Pydantic model: request ka structure define karta hai ---
class QueryRequest(BaseModel):
    question: str


# --- Pydantic model: response ka structure define karta hai ---
class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


@app.get("/health")
def health_check():
    """
    Simple endpoint jo check karta hai ki server chal raha hai ya nahi.
    """
    return {"status": "ok", "chunks_loaded": len(all_points)}


@app.post("/query")
def query(request: QueryRequest):
    """
    Main endpoint - question leta hai, poora pipeline chalata hai,
    aur answer + sources wapas deta hai.
    """
    question = request.question

    # Step 1: Retrieval (query expansion + hybrid search + rerank)
    candidates = multi_query_hybrid_search(question, all_points, top_k=10)
    top_chunks = rerank(question, candidates, top_k=5)

    # Step 2: Generation
    answer = generate_answer(question, top_chunks)

    # Sources ki list nikal lo (duplicate hata ke)
    sources = list(set([c["source"] for c in top_chunks]))

    return QueryResponse(
        question=question,
        answer=answer,
        sources=sources,
    )