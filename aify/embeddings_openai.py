import os
import openai


def embed(text: str, model='text-embedding-ada-002'):
    """Generate embeddings."""
    if "OPENAI_API_KEY" in os.environ:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    if "OPENAI_API_BASE" in os.environ:
        openai.api_base = os.environ["OPENAI_API_BASE"]

    return openai.Embedding.create(
        input=[text],
        model=model
    )['data'][0]['embedding']
