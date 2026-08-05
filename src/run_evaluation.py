import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from data.eval_questions import EVAL_QUESTIONS
from hybrid_search import load_all_chunks, multi_query_hybrid_search, rerank
from generate_answer import generate_answer

import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def score_faithfulness(answer, context):
    """
    LLM se poochte hain: kya ye answer sirf diye gaye context se aaya hai,
    ya kuch extra bana diya gaya (hallucinate kiya)?
    Score: 0.0 (bilkul faithful nahi) se 1.0 (poora faithful) tak.
    """
    prompt = f"""You are evaluating whether an AI-generated answer is faithful to the given context (i.e., doesn't contain information not present in the context).

Context:
{context}

Answer:
{answer}

Rate the faithfulness of this answer on a scale of 0.0 to 1.0, where:
- 1.0 = every claim in the answer is directly supported by the context
- 0.0 = the answer contains significant information not found in the context

Respond with ONLY a number between 0.0 and 1.0, nothing else."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    try:
        score = float(response.choices[0].message.content.strip())
        return max(0.0, min(1.0, score))  # 0-1 ke beech clamp kar do
    except ValueError:
        return None


def score_answer_relevancy(question, answer):
    """
    LLM se poochte hain: kya ye answer poochhe gaye sawal ko address karta hai?
    """
    prompt = f"""You are evaluating whether an AI-generated answer is relevant to the question asked.

Question:
{question}

Answer:
{answer}

Rate the relevancy of this answer on a scale of 0.0 to 1.0, where:
- 1.0 = the answer directly and completely addresses the question
- 0.0 = the answer is completely unrelated to the question

Respond with ONLY a number between 0.0 and 1.0, nothing else."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    try:
        score = float(response.choices[0].message.content.strip())
        return max(0.0, min(1.0, score))
    except ValueError:
        return None


def score_context_precision(question, context):
    """
    LLM se poochte hain: kya retrieved context genuinely relevant hai sawal ke liye?
    """
    prompt = f"""You are evaluating whether the retrieved context is relevant to the question asked.

Question:
{question}

Retrieved Context:
{context}

Rate the precision of this context on a scale of 0.0 to 1.0, where:
- 1.0 = the context is highly relevant and useful for answering the question
- 0.0 = the context is completely irrelevant to the question

Respond with ONLY a number between 0.0 and 1.0, nothing else."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    try:
        score = float(response.choices[0].message.content.strip())
        return max(0.0, min(1.0, score))
    except ValueError:
        return None


def run_evaluation():
    print("Loading all chunks from Qdrant...")
    all_points = load_all_chunks()
    print(f"Loaded {len(all_points)} chunks.\n")

    results = []

    for i, item in enumerate(EVAL_QUESTIONS, 1):
        question = item["question"]
        category = item["category"]

        print(f"[{i}/{len(EVAL_QUESTIONS)}] {question}")

        # Retrieval
        candidates = multi_query_hybrid_search(question, all_points, top_k=10)
        top_chunks = rerank(question, candidates, top_k=5)
        context = "\n\n".join([c["text"] for c in top_chunks])

        # Generation
        answer = generate_answer(question, top_chunks)

        # Scoring (teen alag LLM calls, har metric ke liye)
        faithfulness = score_faithfulness(answer, context)
        relevancy = score_answer_relevancy(question, answer)
        precision = score_context_precision(question, context)

        print(f"  Faithfulness: {faithfulness}, Relevancy: {relevancy}, Precision: {precision}\n")

        results.append({
            "question": question,
            "category": category,
            "answer": answer,
            "faithfulness": faithfulness,
            "answer_relevancy": relevancy,
            "context_precision": precision,
        })

    return results


if __name__ == "__main__":
    results = run_evaluation()

    df = pd.DataFrame(results)
    df.to_csv("data/eval_results.csv", index=False)

    print("\n=== OVERALL AVERAGES ===")
    print(f"Faithfulness:      {df['faithfulness'].mean():.2f}")
    print(f"Answer Relevancy:  {df['answer_relevancy'].mean():.2f}")
    print(f"Context Precision: {df['context_precision'].mean():.2f}")

    print("\n=== BY CATEGORY ===")
    print(df.groupby("category")[["faithfulness", "answer_relevancy", "context_precision"]].mean())

    print("\nDetailed results saved to data/eval_results.csv")