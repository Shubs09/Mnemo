from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .dependencies import get_current_user
from .supabase_client import get_user_supabase
from .embeddings import generate_embedding

router = APIRouter(prefix="/journal", tags=["Journal"])


class JournalCreate(BaseModel):
    content: str

class JournalSearch(BaseModel):
    query: str



@router.post("/")
def create_journal(
    journal: JournalCreate,
    current_user=Depends(get_current_user)
):
    try:
        # Generate 384-dimensional embedding from journal text
        embedding = generate_embedding(journal.content)

        # Create Supabase client using the logged-in user's JWT
        user_supabase = get_user_supabase(current_user["token"])

        # Save journal + embedding
        response = (
            user_supabase
            .table("journal_entries")
            .insert({
                "user_id": current_user["user"].id,
                "content": journal.content,
                "embedding": embedding
            })
            .execute()
        )

        return {
            "message": "Journal entry created successfully",
            "journal": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



@router.post("/search")
def search_journals(
    search: JournalSearch,
    current_user=Depends(get_current_user)
):
    try:
        # Get authenticated user's Supabase client
        user_supabase = get_user_supabase(current_user["token"])

        # Convert user's question into a 384-dimensional embedding
        query_embedding = generate_embedding(search.query)

        # Search only this user's journal entries
        response = user_supabase.rpc(
            "match_journals",
            {
                "query_embedding": query_embedding,
                "match_user_id": current_user["user"].id,
                "match_threshold": 0.5,
                "match_count": 5
            }
        ).execute()

        return {
            "query": search.query,
            "results": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )




@router.get("/")
def get_journals(
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user["token"])

        response = (
            user_supabase
            .table("journal_entries")
            .select("*")
            .eq("user_id", current_user["user"].id)
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "journals": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.patch("/{journal_id}")
def update_journal(
    journal_id: int,
    journal: JournalCreate,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user["token"])

        # Generate a new embedding for the updated content
        embedding = generate_embedding(journal.content)

        response = (
            user_supabase
            .table("journal_entries")
            .update({
                "content": journal.content,
                "embedding": embedding
            })
            .eq("id", journal_id)
            .eq("user_id", current_user["user"].id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Journal entry not found"
            )

        return {
            "message": "Journal entry updated successfully",
            "journal": response.data
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{journal_id}")
def delete_journal(
    journal_id: int,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user["token"])

        response = (
            user_supabase
            .table("journal_entries")
            .delete()
            .eq("id", journal_id)
            .eq("user_id", current_user["user"].id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Journal entry not found"
            )

        return {
            "message": "Journal entry deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
