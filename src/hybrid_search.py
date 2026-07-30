from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

COLLECTION_NAME = "razorpay_docs"

# --- Setup: connect to Qdrant and load the embedding model ---
client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_all_chunks():
    """
    Pulls every stored chunk's text + source out of Qdrant, so we can
    build a BM25 index from them. Qdrant is great at vector search, but
    BM25 needs the raw text directly, in memory.
    """
    # scroll() lets us page through ALL points in a collection (not just
    # search results) - we want every single one to build our BM25 index
    all_points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,          # more than enough since we only have 188
        with_payload=True,   # we want the text/source, not just IDs
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
    # We only need each result's point ID, in ranked order
    return [point.id for point in results]


def bm25_search(query, all_points, top_k=20):
    """
    Runs classic keyword search across all chunk texts.
    """
    # Prepare the text corpus: BM25 needs each document split into words
    corpus = [point.payload["text"].split() for point in all_points]
    bm25 = BM25Okapi(corpus)

    # Split the query into words the same way
    query_tokens = query.split()

    # Get BM25 scores for every chunk against this query
    scores = bm25.get_scores(query_tokens)

    # Pair each point's ID with its score, then sort by score (highest first)
    scored_points = list(zip([p.id for p in all_points], scores))
    scored_points.sort(key=lambda x: x[1], reverse=True)

    # Return just the top_k IDs, in ranked order
    return [point_id for point_id, score in scored_points[:top_k]]


def reciprocal_rank_fusion(vector_ids, bm25_ids, k=60):
    """
    Combines two ranked lists into one final ranking using RRF.
    """
    rrf_scores = {}

    # Add scores from vector search ranking
    for rank, point_id in enumerate(vector_ids):
        rrf_scores[point_id] = rrf_scores.get(point_id, 0) + 1 / (k + rank + 1)

    # Add scores from BM25 ranking
    for rank, point_id in enumerate(bm25_ids):
        rrf_scores[point_id] = rrf_scores.get(point_id, 0) + 1 / (k + rank + 1)

    # Sort all chunks by their combined RRF score, highest first
    sorted_ids = sorted(rrf_scores.keys(), key=lambda pid: rrf_scores[pid], reverse=True)
    return sorted_ids


def hybrid_search(query, all_points, top_k=10):
    """
    The main function: runs both search methods, combines them, and
    returns the final top chunks with their actual text.
    """
    vector_ids = vector_search(query, top_k=20)
    bm25_ids = bm25_search(query, all_points, top_k=20)

    combined_ids = reciprocal_rank_fusion(vector_ids, bm25_ids)
    top_ids = combined_ids[:top_k]

    # Look up the actual text/source for each winning ID
    id_to_point = {point.id: point for point in all_points}
    results = []
    for point_id in top_ids:
        point = id_to_point[point_id]
        results.append({
            "text": point.payload["text"],
            "source": point.payload["source"],
        })
    return results


# --- Test it out ---
if __name__ == "__main__":
    print("Loading all chunks from Qdrant...")
    all_points = load_all_chunks()
    print(f"Loaded {len(all_points)} chunks.\n")

    test_query = "What happens if I don't collect the money from a customer in time?"
    print(f"Query: {test_query}\n")

    results = hybrid_search(test_query, all_points, top_k=5)

    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (source: {r['source']}) ---")
        print(r["text"][:200] + "...")
        print()