import os
from dotenv import load_dotenv
from groq import Groq

# Import our existing retrieval functions from Day 3/4's file
from hybrid_search import load_all_chunks, hybrid_search, rerank

# Load environment variables (our API key) from .env
load_dotenv()

# Create a connection to Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(question, chunks):
    """
    Takes the user's question and the retrieved chunks, and builds
    the full instruction text (prompt) to send to the LLM.
    """
    # Build the "Context" section by joining all chunks together,
    # each labeled with its source file
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"{chunk['text']}\n(Source: {chunk['source']})")

    context = "\n\n".join(context_parts)

    prompt = f"""You are a helpful assistant answering questions about Razorpay's API based ONLY on the provided documentation context below.

Rules:
- Only use information from the context provided below
- If the answer isn't in the context, say "I don't have information on this in the provided documentation"
- Always mention which source document your answer came from
- Be concise and direct

Context:
{context}

Question: {question}

Answer:"""

    return prompt


def generate_answer(question, chunks):
    """
    Sends the built prompt to Groq's LLM and returns the generated answer.
    """
    prompt = build_prompt(question, chunks)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # low temperature = more focused, less "creative"/random
    )

    return response.choices[0].message.content


# --- Test the full pipeline end-to-end ---
if __name__ == "__main__":
    print("Loading all chunks from Qdrant...")
    all_points = load_all_chunks()
    print(f"Loaded {len(all_points)} chunks.\n")

    test_question = "capital of india?"
    print(f"Question: {test_question}\n")

    # Step 1: Retrieve (hybrid search + rerank, from Day 3/4)
    candidates = hybrid_search(test_question, all_points, top_k=10)
    top_chunks = rerank(test_question, candidates, top_k=5)

    print("Retrieved chunks from:")
    for c in top_chunks:
        print(f"  - {c['source']}")

    # Step 2: Generate (new, today's step)
    print("\nGenerating answer...\n")
    answer = generate_answer(test_question, top_chunks)

    print("=== ANSWER ===")
    print(answer)