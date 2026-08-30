import re

PATTERNS = {
    "EMAIL":    re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "PHONE_IN": re.compile(r"(?<!\d)(?:\+91[\-\s]?)?[6-9]\d{9}(?!\d)"),
    "CREDIT_CARD": re.compile(r"(?<!\d)(?:\d[ -]*?){13,16}(?!\d)"),
    "AADHAAR":  re.compile(r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)"),
    "PAN_IN":   re.compile(r"[A-Z]{5}\d{4}[A-Z]"),
}

def luhn_valid(card_str: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", card_str)]
    if not (13 <= len(digits) <= 16):
        return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9: d -= 9
        checksum += d
    return checksum % 10 == 0

def detect_and_tokenize(text: str) -> tuple[str, dict]:
    """Returns (redacted_text, findings). findings = {"EMAIL": 1, "CREDIT_CARD": 1, ...}"""
    findings = {}
    redacted = text
    counters = {}

    for label, pattern in PATTERNS.items():
        matches = list(pattern.finditer(redacted))
        for m in matches:
            if label == "CREDIT_CARD" and not luhn_valid(m.group()):
                continue  # avoid false-positives on random 16-digit numbers
            counters[label] = counters.get(label, 0) + 1
            token = f"[PII:{label}_{counters[label]}]"
            redacted = redacted.replace(m.group(), token, 1)
            findings[label] = findings.get(label, 0) + 1

    return redacted, findings
