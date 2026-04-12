from typing import List, Dict
import ollama
import logging
import os

logger = logging.getLogger(__name__)


MODEL_CANDIDATES = [
    os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    "llama3.2:3b",
    "llama3",
    "mistral",
    "llama2",
]


def _get_available_models() -> List[str]:
    try:
        models_response = ollama.list()
        return [item["model"] for item in models_response.get("models", [])]
    except Exception as e:
        logger.warning(f"Could not fetch Ollama model list: {e}")
        return []


def _pick_model() -> str:
    available_models = _get_available_models()

    if not available_models:
        return MODEL_CANDIDATES[0]

    for preferred in MODEL_CANDIDATES:
        if preferred in available_models:
            return preferred

    return available_models[0]


def generate_answer(question: str, context_chunks: List[str], history: List[Dict[str, str]] | None = None) -> str:
    """
    Generate an answer using Ollama LLM based on context chunks.
    
    Args:
        question: The user's question
        context_chunks: List of relevant document chunks
        history: Recent conversation turns
        
    Returns:
        Generated answer as a string
    """
    if not context_chunks:
        return "I don't have enough information to answer your question."

    # Build context
    context = "\n\n".join(context_chunks)

    history = history or []
    history_lines = []
    for turn in history[-8:]:
        role = turn.get("role", "user")
        text = turn.get("text", "").strip()
        if not text:
            continue
        speaker = "User" if role == "user" else "Assistant"
        history_lines.append(f"{speaker}: {text}")

    conversation_history = "\n".join(history_lines) if history_lines else "(no prior conversation)"
    
    # Limit context length to prevent token overflow
    max_context_length = 4000
    if len(context) > max_context_length:
        context = context[:max_context_length] + "..."

    system_prompt = """You are a helpful, clear, and structured assistant.

Rules you must follow:
1) Use only the provided context.
2) If context is insufficient, say: I don't know based on the provided documents.
3) Be direct, accurate, and easy to read.
4) Prefer short paragraphs and bullet points when useful.
5) Do not invent facts that are not present in context.
6) Keep continuity with conversation history when answering follow-up questions.
"""

    user_prompt = f"""Conversation history:
{conversation_history}

Context:
{context}

Question:
{question}

Provide the best grounded answer."""

    try:
        selected_model = _pick_model()
        logger.info(f"Calling Ollama with model: {selected_model}")

        response = ollama.chat(
            model=selected_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            options={
                "temperature": 0.35,
                "top_p": 0.9,
            },
        )

        answer = response["message"]["content"].strip()
        
        if not answer:
            logger.warning("Empty response from Ollama")
            return "I couldn't generate a response. Please try again."
        
        logger.info("Answer generated successfully")
        return answer

    except Exception as e:
        logger.error(f"Primary generation error: {e}")

        # Last-attempt fallback with a lightweight model if available.
        try:
            fallback_model = "llama3.2:3b"
            logger.info(f"Retrying Ollama with fallback model: {fallback_model}")
            fallback_response = ollama.chat(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                options={"temperature": 0.2},
            )
            fallback_answer = fallback_response["message"]["content"].strip()
            if fallback_answer:
                return fallback_answer
        except Exception as fallback_error:
            logger.error(f"Fallback generation error: {fallback_error}")

        return "I encountered an error while generating a response. Please retry, and if it continues, restart Ollama."
