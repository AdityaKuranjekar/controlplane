from gateway.agent.sandbox import TOOL_REGISTRY
from gateway.agent.action_gateway import scan_tool_output_for_injection

def test_scanner():
    clean_content = TOOL_REGISTRY["read_file"](path="invoice_clean.txt")
    injected_content = TOOL_REGISTRY["read_file"](path="invoice_injected.txt")
    
    assert not scan_tool_output_for_injection(clean_content), "Scanner incorrectly flagged clean content!"
    assert scan_tool_output_for_injection(injected_content), "Scanner FAILED to flag injected content!"
    print("test_injection_scanner.py PASSED. Scanner correctly matched fixture strings.")

if __name__ == "__main__":
    test_scanner()
