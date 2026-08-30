import os
from dotenv import load_dotenv
load_dotenv()

import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from gateway.schemas import ChatCompletionRequest, RiskVector
from gateway.pregate.pii import detect_and_tokenize
from gateway.pregate.injection import injection_score
from gateway.policy.engine import get_profile
from gateway.decision.engine import decide
from gateway.timing import Stopwatch
from gateway.audit.chain import append_row
from gateway.audit.db import init_db
from gateway.llm.groq_client import stream_completion
from gateway.cache.semantic_cache import cache_lookup, cache_store
from gateway.router.cascade import run_cascade
from gateway.ground.grounding_gate import GroundingGate          # ADDED for L2

app = FastAPI()
init_db()

def _chunk_answer_for_streaming(answer: str, chunk_size: int = 4):  # ADDED for L2
    words = answer.split(" ")
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size]) + " "

# Warm models removed for Cloud-Lite

@app.post("/v1/chat/completions")
async def chat(req: ChatCompletionRequest):
    sw = Stopwatch()
    profile = get_profile(req.cp_profile)
    user_msg = req.messages[-1].content

    with sw.measure("pii"):
        redacted, pii_findings = detect_and_tokenize(user_msg)

    with sw.measure("injection"):
        safety_score = injection_score(redacted)

    risk = RiskVector(
        privacy=1.0 if pii_findings else 0.0,
        safety=safety_score,
    )
    decision = decide(risk, profile)

    row_hash = append_row(
        profile=req.cp_profile, prompt_redacted=redacted,
        action=decision.action, reason=decision.reason,
        risk_vector=risk.model_dump(), latency_ms=sw.stages,
    )

    headers = sw.as_headers()
    headers["X-CP-Action"] = decision.action
    headers["X-CP-Audit-Hash"] = row_hash[:16]

    if decision.action == "BLOCK":
        if not req.stream:
            return JSONResponse(content={"choices": [{"message": {"content": f"[BLOCKED: {decision.reason}]"}}]}, headers=headers)
        async def blocked():
            yield f"data: [BLOCKED: {decision.reason}]\n\n"
        return StreamingResponse(blocked(), headers=headers, media_type="text/event-stream")

    messages = [{"role": m.role, "content": redacted if m is req.messages[-1] else m.content} for m in req.messages]

    with sw.measure("cache_lookup"):
        cached = cache_lookup(redacted, req.cp_profile)

    if cached:
        headers = sw.as_headers()
        headers["X-CP-Action"] = decision.action
        headers["X-CP-Audit-Hash"] = row_hash[:16]
        headers["X-CP-Cache"] = "HIT"
        headers["X-CP-Cache-Sim"] = f"{cached['similarity']:.3f}"

        if not req.stream:
            return JSONResponse(content={"choices": [{"message": {"content": cached['response']}}]}, headers=headers)
        async def cached_stream():
            yield f"data: {cached['response']}\n\n"
        return StreamingResponse(cached_stream(), headers=headers, media_type="text/event-stream")

    headers["X-CP-Cache"] = "MISS"
    with sw.measure("cascade"):
        result = await run_cascade(messages)

    headers = sw.as_headers()
    headers["X-CP-Action"] = decision.action
    headers["X-CP-Audit-Hash"] = row_hash[:16]
    headers["X-CP-Cache"] = "MISS"
    headers["X-CP-Tier"] = result["tier_used"]
    headers["X-CP-Escalated"] = str(result["escalated"])

    cache_store(redacted, result["answer"], result["tier_used"])

    # ADDED for L2: grounding gate, only for internal_rag profile with context supplied
    if req.cp_profile == "internal_rag" and req.context_chunks:
        with sw.measure("grounding_setup"):
            gate = GroundingGate(req.context_chunks, threshold=profile.get("grounding_threshold", 0.6))
        claim_events = []

        async def generate_grounded():
            for char_chunk in _chunk_answer_for_streaming(result["answer"]):
                yield f"data: {char_chunk}\n\n"
                events = gate.feed_token(char_chunk)
                for ev in events:
                    claim_events.append(ev)
                    yield f"event: claim_checked\ndata: {json.dumps(ev)}\n\n"
            tail_event = gate.finalize()
            if tail_event:
                claim_events.append(tail_event)
                yield f"event: claim_checked\ndata: {json.dumps(tail_event)}\n\n"

        headers["X-CP-Grounding-Risk"] = f"{gate.grounding_risk():.3f}" if claim_events else "n/a"
        return StreamingResponse(generate_grounded(), headers=headers, media_type="text/event-stream")

    if not req.stream:
        return JSONResponse(content={"choices": [{"message": {"content": result['answer']}}]}, headers=headers)

    async def generate():
        yield f"data: {result['answer']}\n\n"

    return StreamingResponse(generate(), headers=headers, media_type="text/event-stream")

@app.get("/v1/audit/logs")
async def get_audit_logs():
    import sqlite3
    try:
        conn = sqlite3.connect("audit.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_log ORDER BY id ASC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"logs": rows}
    except Exception as e:
        return {"logs": [], "error": str(e)}

@app.get("/v1/grounding/calibration")
async def get_calibration():
    import json
    import os
    try:
        cal = json.load(open("eval/results/l2_calibration.json"))
        met = json.load(open("eval/results/l2_metrics.json"))
        return {"calibration": cal, "metrics": met}
    except Exception as e:
        return {"error": str(e)}

@app.get("/v1/routing/bandit")
async def get_bandit():
    import json
    import os
    try:
        return json.load(open("eval/results/l4_bandit_metrics.json"))
    except Exception as e:
        return {"error": str(e)}
