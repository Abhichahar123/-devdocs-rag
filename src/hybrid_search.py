from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from query_expansion import expand_query

COLLECTION_NAME = "razorpay_docs"

# --- Setup: connect to Qdrant and load models ---
client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def load_all_chunks():
    """
    Pulls every stored chunk's text + source out of Qdrant, so we can
    build a BM25 index from them.
    """
    all_points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        with_payload=True,
    )
    return all_points


def vector_search(query, top_k=20):
    """
    Embeds the user's question, then asks Qdrant for the most
    similar chunks by meaning.
    """
    query_vector = model.encode(query).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )
    return [point.id for point in results]


def bm25_search(query, all_points, top_k=20):
    """
    Runs classic keyword search across all chunk texts.
    """
    corpus = [point.payload["text"].split() for point in all_points]
    bm25 = BM25Okapi(corpus)

    query_tokens = query.split()
    scores = bm25.get_scores(query_tokens)

    scored_points = list(zip([p.id for p in all_points], scores))
    scored_points.sort(key=lambda x: x[1], reverse=True)

    return [point_id for point_id, score in scored_points[:top_k]]


def reciprocal_rank_fusion(vector_ids, bm25_ids, k=60):
    """
    Combines two ranked lists into one final ranking using RRF.
    """
    rrf_scores = {}

    for rank, point_id in enumerate(vector_ids):
        rrf_scores[point_id] = rrf_scores.get(point_id, 0) + 1 / (k + rank + 1)

    for rank, point_id in enumerate(bm25_ids):
        rrf_scores[point_id] = rrf_scores.get(point_id, 0) + 1 / (k + rank + 1)

    sorted_ids = sorted(rrf_scores.keys(), key=lambda pid: rrf_scores[pid], reverse=True)
    return sorted_ids


def hybrid_search(query, all_points, top_k=10):
    """
    Runs both search methods, combines them, and returns the final
    top chunks with their actual text.
    """
    vector_ids = vector_search(query, top_k=20)
    bm25_ids = bm25_search(query, all_points, top_k=20)

    combined_ids = reciprocal_rank_fusion(vector_ids, bm25_ids)
    top_ids = combined_ids[:top_k]

    id_to_point = {point.id: point for point in all_points}
    results = []
    for point_id in top_ids:
        point = id_to_point[point_id]
        results.append({
            "text": point.payload["text"],
            "source": point.payload["source"],
        })
    return results


def multi_query_hybrid_search(original_question, all_points, top_k=10):
    """
    Expands the original question into multiple phrasings, runs hybrid
    search for each, and combines all results together using RRF.
    """
    variations = expand_query(original_question, num_variations=3)
    all_questions = [original_question] + variations

    all_ranked_lists = []
    for question in all_questions:
        vector_ids = vector_search(question, top_k=20)
        bm25_ids = bm25_search(question, all_points, top_k=20)
        all_ranked_lists.append(vector_ids)
        all_ranked_lists.append(bm25_ids)

    rrf_scores = {}
    k = 60
    for ranked_list in all_ranked_lists:
        for rank, point_id in enumerate(ranked_list):
            rrf_scores[point_id] = rrf_scores.get(point_id, 0) + 1 / (k + rank + 1)

    sorted_ids = sorted(rrf_scores.keys(), key=lambda pid: rrf_scores[pid], reverse=True)
    top_ids = sorted_ids[:top_k]

    id_to_point = {point.id: point for point in all_points}
    results = []
    for point_id in top_ids:
        point = id_to_point[point_id]
        results.append({
            "text": point.payload["text"],
            "source": point.payload["source"],
        })
    return results


def rerank(query, candidates, top_k=5):
    """
    Re-scores hybrid search candidates by reading the query and each
    chunk together (cross-encoder), returning the top_k best matches.
    """
    pairs = [[query, c["text"]] for c in candidates]
    scores = reranker.predict(pairs)

    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    reranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
    return reranked[:top_k]


# --- Test it out ---
if __name__ == "__main__":
    print("Loading all chunks from Qdrant...")
    all_points = load_all_chunks()
    print(f"Loaded {len(all_points)} chunks.\n")

    test_query = "What happens if I don't collect the money from a customer in time?"
    print(f"Query: {test_query}\n")

    print("=== WITHOUT query expansion (original hybrid search) ===")
    candidates_before = hybrid_search(test_query, all_points, top_k=10)
    for i, c in enumerate(candidates_before, 1):
        print(f"{i}. [{c['source']}] {c['text'][:100]}...")

    print("\n=== WITH query expansion ===")
    candidates_after = multi_query_hybrid_search(test_query, all_points, top_k=10)
    for i, c in enumerate(candidates_after, 1):
        print(f"{i}. [{c['source']}] {c['text'][:100]}...")

    final_results = rerank(test_query, candidates_after, top_k=5)
    print("\n=== After reranking (final answer-ready chunks) ===")
    for i, r in enumerate(final_results, 1):
        print(f"{i}. [score: {r['rerank_score']:.2f}] [{r['source']}] {r['text'][:100]}...")