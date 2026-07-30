import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import nltk
from nltk.tokenize import sent_tokenize

# --- Configuration ---
RAW_DATA_DIR = "data/raw"
CHUNK_SIZE = 500        # target characters per chunk
CHUNK_OVERLAP = 50       # characters of overlap between chunks
COLLECTION_NAME = "razorpay_docs"

# --- Step 1: Load the embedding model ---
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")

# --- Step 2: Connect to Qdrant (running via Docker) ---
client = QdrantClient(host="localhost", port=6333)

# --- Step 3: Create a "collection" in Qdrant to store our chunks ---
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)
print(f"Collection '{COLLECTION_NAME}' created in Qdrant.")


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Splits text into overlapping chunks, breaking at sentence boundaries
    where possible instead of cutting mid-sentence.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] + " " + sentence
        else:
            current_chunk += " " + sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# --- Step 4: Process every raw file ---
all_points = []
point_id = 0

filenames = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".txt")]
print(f"Found {len(filenames)} files to process.")

for filename in filenames:
    filepath = os.path.join(RAW_DATA_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    print(f"  {filename}: split into {len(chunks)} chunks")

    for chunk in chunks:
        embedding = model.encode(chunk).tolist()

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": chunk,
                "source": filename,
            },
        )
        all_points.append(point)
        point_id += 1

# --- Step 5: Upload everything to Qdrant in one batch ---
client.upsert(collection_name=COLLECTION_NAME, points=all_points)

print(f"\nDone! Stored {len(all_points)} chunks in Qdrant collection '{COLLECTION_NAME}'.")