from gateway.decision.engine import decide
from gateway.schemas import RiskVector
from gateway.policy.engine import get_profile

def test_decision_block_on_injection():
    profile = get_profile("customer_bot")
    risk = RiskVector(privacy=0.0, safety=0.8)
    decision = decide(risk, profile)
    assert decision.action == "BLOCK"

def test_decision_redact_on_pii():
    profile = get_profile("customer_bot")
    risk = RiskVector(privacy=1.0, safety=0.0)
    decision = decide(risk, profile)
    assert decision.action == "REDACT"

def test_decision_allow_on_clean():
    profile = get_profile("customer_bot")
    risk = RiskVector(privacy=0.0, safety=0.0)
    decision = decide(risk, profile)
    assert decision.action == "ALLOW"

