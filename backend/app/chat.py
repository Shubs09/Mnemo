from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .dependencies import get_current_user
from .supabase_client import get_user_supabase
from .embeddings import generate_embedding
from .llm_client import generate_answer


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str


@router.post("/")
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    try:
        # Get Supabase client using the authenticated user's JWT
        user_supabase = get_user_supabase(current_user["token"])

        # Convert the user's question into an embedding
        query_embedding = generate_embedding(request.query)

        # Search only this user's journal entries
        search_response = user_supabase.rpc(
            "match_journals",
            {
                "query_embedding": query_embedding,
                "match_user_id": current_user["user"].id,
                "match_threshold": 0.5,
                "match_count": 5
            }
        ).execute()

        journals = search_response.data

        # No relevant journal entries found
        if not journals:
            return {
                "query": request.query,
                "answer": "I could not find anything relevant in your journal."
            }

        # Build context from retrieved journal entries
        context = "\n\n".join(
            [
                f"Journal entry {journal['id']}: {journal['content']}"
                for journal in journals
            ]
        )

        # Send retrieved context + question to the LLM
        answer = generate_answer(
            question=request.query,
            context=context
        )

        return {
            "query": request.query,
            "answer": answer,
            "sources": journals
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )