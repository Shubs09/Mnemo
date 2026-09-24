from openai import OpenAI

from .config import (
    LLM_PROVIDER,
    LLM_BASE_URL,
    LLM_API_KEY,
    LLM_MODEL,
)


def get_llm_client():
    """
    Create an OpenAI-compatible client.

    Supported providers:
    - OpenRouter
    - Ollama
    """

    if LLM_PROVIDER not in {"openrouter", "ollama"}:
        raise ValueError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )

    # Ollama does not require a real API key.
    api_key = LLM_API_KEY

    if LLM_PROVIDER == "ollama" and not api_key:
        api_key = "ollama"

    return OpenAI(
        base_url=LLM_BASE_URL,
        api_key=api_key,
    )


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer using only the retrieved journal context.
    """

    client = get_llm_client()

    system_prompt = """
You are a personalized AI journal assistant.

Answer the user's question ONLY using the journal
entries provided in the context.

Rules:
1. Do not use outside knowledge to answer personal-memory questions.
2. Do not invent or assume information.
3. If the answer cannot be found in the provided journal context,
   clearly say that you could not find it in the user's journal.
4. Keep the answer concise and natural.
5. Treat the journal context as private user information.
"""

    user_prompt = f"""
Journal context:

{context}

User question:

{question}

Answer the question using only the journal context.
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content