import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def expand_query(question, num_variations=3):
    """
    Asks the LLM to generate alternative phrasings of the question,
    using more formal/documentation-style language, to help retrieval
    catch questions worded very differently from the source docs.
    """
    prompt = f"""Given this user question about Razorpay's payment API, generate {num_variations} alternative phrasings that use more formal, technical, documentation-style language. Each rewrite should preserve the original meaning but use different words/phrasing that might match how official API documentation would describe the same concept.

Return ONLY the {num_variations} rewrites, one per line, no numbering, no extra text.

Original question: {question}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,  # a bit higher than generation - we WANT some variety here
    )

    raw_text = response.choices[0].message.content
    # Split the response into individual lines, remove empty ones
    variations = [line.strip() for line in raw_text.split("\n") if line.strip()]

    return variations


# --- Test it ---
if __name__ == "__main__":
    test_question = "What happens if I don't collect the money from a customer in time?"

    print(f"Original question: {test_question}\n")
    print("Generating alternative phrasings...\n")

    variations = expand_query(test_question)

    print("Alternative phrasings generated:")
    for i, v in enumerate(variations, 1):
        print(f"{i}. {v}")