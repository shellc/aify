import os
import pandas as pd
import numpy as np

from . import embeddings_openai
from . import _env


def embed(text: str, max_length=None):
    """Genereate embeddings.

    Only OpenAI is currently supported.
    """
    return embeddings_openai.embed(text=text if not max_length else text[:max_length])


def cosine_similarity(a, b):
    """This is the Cosine Similarity algorithm."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search(collection_name: str, text: str, n=3):
    """Searches the specified collection."""
    df = _load_collections(collection_name)
    embeds = embed(text)
    df['similarities'] = df['embedding'].apply(
        lambda x: cosine_similarity(x, embeds))
    res = df.sort_values('similarities', ascending=False).head(
        n).drop(['embedding'], axis=1)
    return res.values.tolist()


def build_csv(from_file: str, to_file: str):
    """Builds word embeddings for a CSV file"""
    try:
        df = pd.read_csv(from_file)
        df['embedding'] = df.apply(lambda x: embed(x.to_string()), axis=1)
        df.to_csv(to_file, index=False)
    except Exception as e:
        print(e)


_embeds = {}


def _load_collections(name: str):
    global _embeds
    if name not in _embeds:
        csv_file = os.path.join(_env.apps_dir(), 'embeddings', f'{name}.csv')
        if os.path.exists(f"{csv_file}.gz"):
            csv_file = f"{csv_file}.gz"

        df = pd.read_csv(csv_file)
        df['embedding'] = df['embedding'].apply(eval).apply(np.array)
        _embeds[name] = df
    return _embeds[name]
