from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def create_embeddings(texts):
    """
    Convert text chunks into numerical embeddings.

    Args:
        texts: List of text strings.

    Returns:
        List of embedding vectors.
    """

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings