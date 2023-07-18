import os
import json
import pandas as pd
import numpy as np

from . import embeddings_openai
from . import _env

def embed(text: str):
    return embeddings_openai.embed(text=text)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search(collection_name:str, text: str, n=3):
    df = _load(collection_name)
    embeds = embed(text)
    df['similarities'] = df['embedding'].apply(lambda x:cosine_similarity(x, embeds))
    res = df.sort_values('similarities', ascending=False).head(n).drop(['embedding'], axis=1)
    return res.values.tolist()

def build_csv(from_file: str, to_file: str):
    try:
        df = pd.read_csv(from_file)
        df['embedding'] = df.apply(lambda x : embed(x.to_string()), axis=1)
        df.to_csv(to_file, index=False)
    except Exception as e:
        print(e)

_embeds = {}

def _load(name: str):
    global _embeds
    if name not in _embeds:
        df = pd.read_csv(os.path.join(_env.get_apps_dir(), 'embeddings', f'{name}.csv'))
        df['embedding'] = df['embedding'].apply(eval).apply(np.array)
        _embeds[name] = df
    return _embeds[name]