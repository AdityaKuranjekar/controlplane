from sentence_transformers import SentenceTransformer
import numpy as np
from functools import lru_cache

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    # Loaded once per process. ~90MB, ~1-2s cold load, then reused.
    return SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> np.ndarray:
    model = get_model()
    vec = model.encode(text, normalize_embeddings=True)  # unit-norm -> cosine == dot product
    return vec.astype("float32")

def embed_batch(texts: list[str]) -> np.ndarray:
    model = get_model()
    return model.encode(texts, normalize_embeddings=True, batch_size=32).astype("float32")
