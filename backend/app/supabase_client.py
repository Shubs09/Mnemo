from supabase import create_client

from .config import SUPABASE_URL, SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user_supabase(token: str):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    client.postgrest.auth(token)

    return client