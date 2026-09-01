import re

PATTERNS = {
    "SSN":         re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b|\b(?:\d[ -]*?){13,19}\b"),
    "EMAIL":       re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}\b"),
    "PHONE":       re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b(?:\+91[\-\s]?)?[6-9]\d{9}\b"),
    "AADHAAR":     re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "PAN_IN":      re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
}

def luhn_valid(card_str: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", card_str)]
    if not (13 <= len(digits) <= 19):
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
            matched_str = m.group()
            if label == "CREDIT_CARD":
                raw_digits = re.sub(r"\D", "", matched_str)
                if len(raw_digits) not in [13, 15, 16] and not luhn_valid(matched_str):
                    continue
            counters[label] = counters.get(label, 0) + 1
            token = f"[PII:{label}_{counters[label]}]"
            redacted = redacted.replace(matched_str, token, 1)
            findings[label] = findings.get(label, 0) + 1

    return redacted, findings

