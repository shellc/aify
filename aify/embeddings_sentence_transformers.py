from sentence_transformers import SentenceTransformer

_models = {}

def _get_model(model_name):
    if model_name not in _models:
        _models[model_name] = SentenceTransformer(model_name)
    return _models[model_name]

def embed(text: str, model=None):
    model_name = model if model is not None else "all-MiniLM-L6-v2"
    return _get_model(model_name).encode([text], convert_to_tensor=False)[0].tolist()

async def aembed(text: str, model=None):
    model_name = model if model is not None else "all-MiniLM-L6-v2"
    return _get_model(model_name).encode([text], convert_to_tensor=False)[0].tolist()