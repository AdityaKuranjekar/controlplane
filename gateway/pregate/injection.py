INJECTION_MARKERS = [
    "ignore previous instructions", "ignore the above", "system:",
    "you are now", "disregard your instructions", "reveal your prompt",
    "act as", "jailbreak", "developer mode",
]

def injection_score(text: str) -> float:
    t = text.lower()
    hits = sum(1 for m in INJECTION_MARKERS if m in t)
    return min(1.0, hits * 0.4)
