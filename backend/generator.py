from typing import List
import ollama


def generate_answer(question: str, context_chunks: List[str]) -> str:
    if not context_chunks:
        return "I don't know based on the provided documents."

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful assistant.
Answer the question ONLY using the context below.
If the answer is not present, say "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

    response = ollama.chat(
        model="llama3",   # 👈 THIS is the only change
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"].strip()
