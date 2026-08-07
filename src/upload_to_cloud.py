import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import nltk
from nltk.tokenize import sent_tokenize

load_dotenv()

RAW_DATA_DIR = "data/raw"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
COLLECTION_NAME = "razorpay_docs"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")

# --- Yahan farak hai: local ke bajaye, Qdrant Cloud se connect kar rahe hain ---
client = QdrantClient(
    url=os.getenv("QDRANT_CLOUD_URL"),
    api_key=os.getenv("QDRANT_CLOUD_API_KEY"),
)

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)
print(f"Collection '{COLLECTION_NAME}' created on Qdrant Cloud.")


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
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

# Ek hi baar mein saara data bhejne ke bajaye, chhote batches mein bhejte hain
BATCH_SIZE = 25

for i in range(0, len(all_points), BATCH_SIZE):
    batch = all_points[i:i + BATCH_SIZE]
    client.upsert(collection_name=COLLECTION_NAME, points=batch)
    print(f"  Uploaded batch {i // BATCH_SIZE + 1} ({len(batch)} points)")

print(f"\nDone! Stored {len(all_points)} chunks on Qdrant Cloud.")