from gateway.schemas import IntentContract, ToolCall, ActionVerdict
from .sandbox import TOOL_REGISTRY
from .state import is_stale
from gateway.audit.chain import append_row
import json

INJECTION_MARKERS_IN_TOOL_OUTPUT = [
    "system override", "ignore prior instructions", "ignore previous instructions",
    "call send_email", "immediately", "system:", "you must now",
]

def scan_tool_output_for_injection(output: str) -> bool:
    out_lower = str(output).lower()
    return any(marker in out_lower for marker in INJECTION_MARKERS_IN_TOOL_OUTPUT)


class ActionGateway:
    def __init__(self, contract: IntentContract):
        self.contract = contract
        self.write_ops_used = 0
        self.calls_made = 0
        self.tainted = False  # set True once an injection is detected in any tool output this task

    def validate_and_execute(self, call: ToolCall) -> tuple[ActionVerdict, any]:
        """
        Returns (verdict, tool_result). tool_result is None if action != ALLOW.
        """
        self.calls_made += 1

        # Rule 1: hard call-count ceiling (prevents runaway loops)
        if self.calls_made > self.contract.max_tool_calls:
            return self._block(call, "exceeded max_tool_calls ceiling", "max_tool_calls"), None

        # Rule 2: tool must be in the declared allowlist
        if call.tool_name not in self.contract.allowed_tools:
            return self._block(call, f"tool '{call.tool_name}' not in allowed_tools", "allowed_tools"), None

        # Rule 3: if this task has been tainted by a prior injection, block ALL further
        # write-capable actions immediately
        WRITE_TOOLS = {"send_email", "transfer_funds", "update_record"}
        if self.tainted and call.tool_name in WRITE_TOOLS:
            return self._block(call, "task tainted by prior injection; write actions suspended", "tainted_state"), None

        # Rule 4: egress domain check (for send_email specifically)
        if call.tool_name == "send_email":
            to_domain = call.arguments.get("to", "").split("@")[-1]
            if to_domain not in self.contract.allowed_egress_domains:
                return self._block(call, f"egress domain '{to_domain}' not allowlisted", "allowed_egress_domains"), None

        # Rule 5: write-op budget
        if call.tool_name in WRITE_TOOLS:
            if self.write_ops_used >= self.contract.max_write_ops:
                return self._block(call, "exceeded max_write_ops budget", "max_write_ops"), None

        # Rule 6: high-value transfer needs a human, not autonomous approval
        if call.tool_name == "transfer_funds":
            amount = call.arguments.get("amount", 0)
            if self.contract.requires_human_above_amount and amount > self.contract.requires_human_above_amount:
                verdict = ActionVerdict(action="ABSTAIN_NEEDS_HUMAN", reason=f"amount {amount} exceeds human-review threshold",
                                       tool_call=call, contract_violated="requires_human_above_amount")
                # Also log abstain as block in audit chain
                append_row(
                    profile="decision_agent", prompt_redacted=f"tool_call:{call.tool_name} args:{json.dumps(call.arguments)}",
                    action="ABSTAIN_NEEDS_HUMAN", reason=verdict.reason,
                    risk_vector={"privacy": 0.0, "safety": 1.0, "grounding": 0.0, "cost": 0.0},
                    latency_ms={},
                )
                return verdict, None

        # Rule 7: ETag / stale-state drift check for updates
        if call.tool_name == "update_record":
            resource_id = f"record_{call.arguments.get('record_id')}"
            provided_etag = call.arguments.get("etag")
            if is_stale(resource_id, provided_etag):
                return self._block(call, "stale ETag: resource changed since last read, aborting write", "state_drift"), None

        # All checks passed -> EXECUTE via sandbox, then scan the OUTPUT for injection
        result = TOOL_REGISTRY[call.tool_name](**call.arguments)

        if call.tool_name in {"read_file", "search_db"} and scan_tool_output_for_injection(result):
            self.tainted = True  # mark task tainted

        if call.tool_name in WRITE_TOOLS:
            self.write_ops_used += 1

        return ActionVerdict(action="ALLOW", reason="passed all contract checks", tool_call=call), result

    def _block(self, call: ToolCall, reason: str, violated_rule: str) -> ActionVerdict:
        verdict = ActionVerdict(action="BLOCK", reason=reason, tool_call=call, contract_violated=violated_rule)
        append_row(
            profile="decision_agent", prompt_redacted=f"tool_call:{call.tool_name} args:{json.dumps(call.arguments)}",
            action="BLOCK", reason=reason,
            risk_vector={"privacy": 0.0, "safety": 1.0, "grounding": 0.0, "cost": 0.0},
            latency_ms={},
        )
        return verdict
