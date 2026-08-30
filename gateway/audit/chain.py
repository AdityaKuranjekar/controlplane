import hashlib, json, sqlite3
from .db import DB_PATH

def _canonical(row: dict) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"))

def append_row(profile, prompt_redacted, action, reason, risk_vector, latency_ms):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT row_hash FROM audit_log ORDER BY id DESC LIMIT 1")
    prev = cur.fetchone()
    prev_hash = prev[0] if prev else "GENESIS"

    payload = {
        "profile": profile, "prompt_redacted": prompt_redacted,
        "action": action, "reason": reason,
        "risk_vector": risk_vector, "latency_ms": latency_ms,
        "prev_hash": prev_hash,
    }
    row_hash = hashlib.sha256(_canonical(payload).encode()).hexdigest()

    conn.execute(
        "INSERT INTO audit_log (ts, profile, prompt_redacted, action, reason, risk_vector, latency_ms, row_hash, prev_hash) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (__import__("time").time(), profile, prompt_redacted, action, reason,
         json.dumps(risk_vector), json.dumps(latency_ms), row_hash, prev_hash)
    )
    conn.commit()
    conn.close()
    return row_hash
