import os
import openai


def embed(text: str, model='text-embedding-ada-002'):
    """Generate embeddings."""
    openai.api_key = os.environ["OPENAI_API_KEY"]
    openai.api_base = os.environ["OPENAI_API_BASE"]

    return openai.Embedding.create(
        input=[text],
        model=model
    )['data'][0]['embedding']
