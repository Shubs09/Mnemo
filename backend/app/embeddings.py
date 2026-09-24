from sentence_transformers import SentenceTransformer


# Load the embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    """
    Convert text into a 384-dimensional embedding vector.
    """
    embedding = model.encode(text)

    # Convert NumPy array to normal Python list
    return embedding.tolist()