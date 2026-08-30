from pydantic import BaseModel, Field
from typing import Literal, Optional

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "controlplane-default"
    messages: list[ChatMessage]
    stream: bool = True
    cp_profile: Literal["customer_bot", "internal_rag", "decision_agent"] = "customer_bot"
    context_chunks: list[str] = Field(default_factory=list)   # ADDED for L2: retrieved RAG context

class RiskVector(BaseModel):
    privacy: float = 0.0
    safety: float = 0.0
    grounding: float = 0.0
    cost: float = 0.0

class Decision(BaseModel):
    action: Literal["ALLOW", "REDACT", "FLAG", "ABSTAIN", "BLOCK"]
    reason: str
    risk_vector: RiskVector

class CacheMeta(BaseModel):
    query: str
    response: str
    tier_used: str
    hits: int

class ClaimResult(BaseModel):                                  # ADDED for L2
    sentence: str
    score: float | None
    flagged: bool
    best_chunk: str | None

# ADDED FOR L3

class IntentContract(BaseModel):
    """
    Declared upfront, once, at the start of an agent conversation/task.
    Everything the Action Gateway checks a tool call against.
    """
    task_id: str
    allowed_tools: list[str]
    allowed_egress_domains: list[str] = Field(default_factory=list)
    max_write_ops: int = 0
    requires_human_above_amount: float | None = None
    max_tool_calls: int = 10

class ToolCall(BaseModel):
    task_id: str
    tool_name: str
    arguments: dict
    call_index: int

class ActionVerdict(BaseModel):
    action: Literal["ALLOW", "BLOCK", "ABSTAIN_NEEDS_HUMAN"]
    reason: str
    tool_call: ToolCall
    contract_violated: str | None = None
