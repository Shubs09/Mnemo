import os

from dotenv import load_dotenv


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# LLM configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "https://openrouter.ai/api/v1"
)

LLM_API_KEY = os.getenv("LLM_API_KEY")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "openrouter/free"
)