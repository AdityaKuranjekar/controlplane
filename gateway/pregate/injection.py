import re

INJECTION_PATTERNS = [
    re.compile(r"(system|admin|root)[_\s]?override", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(prior|previous|your|directives)", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?(prior|previous|the\s+above|directives|instructions)", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(rules|instructions|directives)", re.IGNORECASE),
    re.compile(r"output\s+(your\s+)?system\s+(prompt|instructions)", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions)", re.IGNORECASE),
    re.compile(r"bypass[_\s]dual[_\s]approval", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"act\s+as\s+(a\s+|an\s+)?(hacker|jailbreak|root|developer|unrestricted AI)", re.IGNORECASE),
    re.compile(r"(jailbreak|dan\s+mode|developer\s+mode(\s+enabled)?)", re.IGNORECASE),
    re.compile(r"simulated\s+mode", re.IGNORECASE),
    re.compile(r"<\/?system>|\[SYSTEM\]|```system", re.IGNORECASE),
    re.compile(r"system:", re.IGNORECASE),
]

def injection_score(text: str, context: str | None = None) -> float:
    combined = f"{text} {context or ''}"
    hits = sum(1 for pattern in INJECTION_PATTERNS if pattern.search(combined))
    if hits > 0:
        return min(1.0, 0.6 + hits * 0.2)
    return 0.0

