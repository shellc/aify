import os
import openai


def _set_env():
    if "OPENAI_API_KEY" in os.environ:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    if "OPENAI_API_BASE" in os.environ:
        openai.api_base = os.environ["OPENAI_API_BASE"]


def embed(text: str, model='text-embedding-ada-002'):
    """Generate embeddings."""
    _set_env()
    return openai.Embedding.create(
        input=[text],
        model=model
    )['data'][0]['embedding']


async def aembed(text: str, model='text-embedding-ada-002'):
    """Generate embeddings."""
    _set_env()
    res = await openai.Embedding.acreate(
        input=[text],
        model=model
    )
    return res['data'][0]['embedding']
