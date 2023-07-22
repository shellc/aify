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

async def aembed(text: str, max_length=None):
    """Genereate embeddings.

    Only OpenAI is currently supported.
    """
    return await embeddings_openai.aembed(text=text if not max_length else text[:max_length])

def cosine_similarity(a, b):
    """This is the Cosine Similarity algorithm."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def _cal_score(collection_name, embeds, limit):
    df = _load_collections(collection_name).copy(deep=False)

    df['score'] = df['embedding'].apply(
        lambda x: cosine_similarity(x, embeds))
    res = df.sort_values('score', ascending=False).head(
        limit).drop(['embedding'], axis=1)
    #return res.values.todict()
    return res.to_json(orient="records", force_ascii=False, double_precision=4)

def search(collection_name: str, text: str, n=3):
    """Searches the specified collection."""
    
    embeds = embed(text)
    
    return _cal_score(collection_name=collection_name, embeds=embeds, limit=n)

async def asearch(collection_name: str, text: str, n=3):
    """Searches the specified collection."""
    
    embeds = await aembed(text)
    
    return _cal_score(collection_name=collection_name, embeds=embeds, limit=n)

def build_csv(from_file: str, to_file: str):
    """Builds word embeddings for a CSV file"""
    try:
        df = pd.read_csv(from_file)
        df['embedding'] = df.apply(lambda x: embed(x.to_string()), axis=1)
        df.to_csv(to_file, index=False)
    except Exception as e:
        print(e)


_embeds = {}

def _load_csv_file(name: str):
    csv_file = os.path.join(_env.apps_dir(), 'embeddings', f'{name}.csv')
    if os.path.exists(f"{csv_file}.gz"):
        csv_file = f"{csv_file}.gz"
    elif not os.path.exists(csv_file):
        return

    df = pd.read_csv(csv_file)
    df['embedding'] = df['embedding'].apply(eval).apply(np.array)

    return df

def _load_pickle_file(name: str):
    pickle_file = os.path.join(_env.apps_dir(), 'embeddings', f'{name}.pkl')
    if os.path.exists(f"{pickle_file}.gz"):
        pickle_file = f"{pickle_file}.gz"
    elif not os.path.exists(pickle_file):
        return

    df = pd.read_pickle(pickle_file)

    return df

def _load_collections(name: str):
    global _embeds
    if name not in _embeds:
        df = _load_pickle_file(name=name)
        if df is None:
            df = _load_csv_file(name=name)

        if df is not None:
            _embeds[name] = df
    return _embeds.get(name)
