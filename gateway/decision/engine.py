from gateway.schemas import RiskVector, Decision

def decide(risk: RiskVector, profile: dict) -> Decision:
    th = profile["thresholds"]
    act = profile["actions"]

    if risk.safety >= th["safety_block"]:
        return Decision(action=act["on_safety_hit"], reason="injection/safety threshold exceeded", risk_vector=risk)

    if risk.privacy > th["privacy_block"]:
        return Decision(action=act["on_privacy_hit"], reason="PII detected and tokenized", risk_vector=risk)

    return Decision(action=act["default"], reason="no risk signals triggered", risk_vector=risk)
