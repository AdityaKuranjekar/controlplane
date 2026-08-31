from gateway.pregate.pii import detect_and_tokenize

def test_ssn_detection():
    text = "My social security number is 123-45-6789."
    redacted, findings = detect_and_tokenize(text)
    assert "SSN" in findings
    assert "123-45-6789" not in redacted
    assert "[PII:SSN_1]" in redacted

def test_credit_card_detection():
    text = "Please charge card 4111111111111111 for the order."
    redacted, findings = detect_and_tokenize(text)
    assert "CREDIT_CARD" in findings
    assert "4111111111111111" not in redacted
    assert "[PII:CREDIT_CARD_1]" in redacted

def test_email_and_phone_detection():
    text = "Contact user at test@example.com or +1 (555) 123-4567."
    redacted, findings = detect_and_tokenize(text)
    assert "EMAIL" in findings
    assert "PHONE" in findings
    assert "test@example.com" not in redacted

