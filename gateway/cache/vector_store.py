import faiss
import numpy as np
import json
import sqlite3
from pathlib import Path

INDEX_PATH = Path("data/cache_index/index.faiss")
META_DB = Path("data/cache_index/meta.db")
DIM = 384  # all-MiniLM-L6-v2 output dim

class VectorStore:
    def __init__(self):
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        if INDEX_PATH.exists():
            self.index = faiss.read_index(str(INDEX_PATH))
        else:
            self.index = faiss.IndexFlatIP(DIM)  # inner product on unit vecs = cosine sim
        self._init_meta_db()

    def _init_meta_db(self):
        conn = sqlite3.connect(META_DB)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_meta (
                faiss_id INTEGER PRIMARY KEY,
                query TEXT, response TEXT,
                tier_used TEXT, created_at REAL, hits INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def search(self, vec: np.ndarray, k: int = 1):
        if self.index.ntotal == 0:
            return [], []
        sims, ids = self.index.search(vec.reshape(1, -1), k)
        return sims[0], ids[0]   # sims are cosine similarities (higher = closer)

    def add(self, vec: np.ndarray, query: str, response: str, tier_used: str):
        faiss_id = self.index.ntotal
        self.index.add(vec.reshape(1, -1))
        conn = sqlite3.connect(META_DB)
        conn.execute(
            "INSERT INTO cache_meta (faiss_id, query, response, tier_used, created_at) VALUES (?,?,?,?,?)",
            (faiss_id, query, response, tier_used, __import__("time").time())
        )
        conn.commit()
        conn.close()
        return faiss_id

    def get_meta(self, faiss_id: int) -> dict | None:
        conn = sqlite3.connect(META_DB)
        row = conn.execute("SELECT query, response, tier_used, hits FROM cache_meta WHERE faiss_id=?", (faiss_id,)).fetchone()
        conn.close()
        if row is None:
            return None
        return {"query": row[0], "response": row[1], "tier_used": row[2], "hits": row[3]}

    def bump_hits(self, faiss_id: int):
        conn = sqlite3.connect(META_DB)
        conn.execute("UPDATE cache_meta SET hits = hits + 1 WHERE faiss_id=?", (faiss_id,))
        conn.commit()
        conn.close()

    def persist(self):
        faiss.write_index(self.index, str(INDEX_PATH))

    def size(self) -> int:
        return self.index.ntotal
