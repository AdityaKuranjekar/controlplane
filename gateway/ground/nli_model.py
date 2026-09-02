import re
from gateway.llm.groq_client import sync_completion

def contradiction_score(premise: str, hypothesis: str) -> float:
    """
    Lite version: Uses Groq API instead of local DeBERTa ONNX model.
    Returns 0.0 (no contradiction) → 1.0 (absolute contradiction).
    """
    prompt = f"""You are a strict logical inference model.
Premise: "{premise}"
Hypothesis: "{hypothesis}"
Does the premise contradict the hypothesis?
Answer ONLY with a number between 0.0 and 1.0, where 1.0 means absolute contradiction and 0.0 means no contradiction."""

    messages = [{"role": "user", "content": prompt}]
    
    try:
        full_response = sync_completion(messages, model="openai/gpt-oss-20b", temperature=0.0)
        
        # Extract first floating point number in [0.0, 1.0]
        match = re.search(r"(?<!\d)(?:0(?:\.\d+)?|1(?:\.0+)?)(?!\d)", full_response.strip())
        if match:
            score = float(match.group(0))
            return min(max(score, 0.0), 1.0)
        
        # Fallback direct float parse
        score = float(full_response.strip())
        return min(max(score, 0.0), 1.0)
    except Exception as e:
        print(f"NLI Fallback due to parsing error: {e}")
        return 0.0


def entailment_score(premise: str, hypothesis: str) -> float:
    """
    Checks whether the premise SUPPORTS / ENTAILS the hypothesis.
    Returns 0.0 (no entailment / completely off-topic) → 1.0 (full entailment).

    Used by GroundingGate's evasion detector: if the LLM's full response
    fails to entail any context chunk (score < 0.25), it is flagged as
    an evasion/grounding failure — even if it didn't explicitly contradict.
    """
    prompt = f"""You are a strict logical inference model.
Premise: "{premise}"
Hypothesis: "{hypothesis}"
Does the premise support or entail the hypothesis? Consider whether the hypothesis is consistent with and relevant to the premise.
Answer ONLY with a number between 0.0 and 1.0, where 1.0 means the premise fully supports the hypothesis and 0.0 means the hypothesis is completely unrelated or unsupported."""

    messages = [{"role": "user", "content": prompt}]

    try:
        full_response = sync_completion(messages, model="openai/gpt-oss-20b", temperature=0.0)

        match = re.search(r"(?<!\d)(?:0(?:\.\d+)?|1(?:\.0+)?)(?!\d)", full_response.strip())
        if match:
            score = float(match.group(0))
            return min(max(score, 0.0), 1.0)

        score = float(full_response.strip())
        return min(max(score, 0.0), 1.0)
    except Exception as e:
        print(f"Entailment NLI Fallback due to parsing error: {e}")
        return 0.5  # neutral fallback — don't false-flag on parse error
