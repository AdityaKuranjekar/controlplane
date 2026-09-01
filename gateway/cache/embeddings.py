import importlib
import hashlib
import numpy as np

_model = None

def embed(text: str) -> np.ndarray:
    """
    Returns a unit-normalized 384-dimensional embedding vector for `text`.
    Attempts to use sentence-transformers if installed; otherwise uses a
    deterministic projection for fast offline replay / testing.
    """
    global _model
    try:
        if _model is None:
            st_module = importlib.import_module("sentence_transformers")
            _model = st_module.SentenceTransformer("all-MiniLM-L6-v2")
        vec = _model.encode(text)
        norm = np.linalg.norm(vec)
        return (vec / norm).astype(np.float32) if norm > 0 else vec.astype(np.float32)
    except Exception:
        pass

    # Deterministic n-gram hash projection fallback (384 dimensions)
    dim = 384
    vec = np.zeros(dim, dtype=np.float32)
    cleaned = text.lower().strip()
    words = cleaned.split()

    for word in words:
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0

    # Include char trigrams for subword / paraphrase similarity
    for i in range(len(cleaned) - 2):
        trigram = cleaned[i:i+3]
        h = int(hashlib.sha256(trigram.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 0.5

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    else:
        vec[0] = 1.0
    return vec
