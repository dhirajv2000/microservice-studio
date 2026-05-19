"""
This is the first node in our graph. I intially coded out some regex checks an typed out some common phrases to reject.
Later found out industry standard libraries which can keep my system more secure. So I chose llm-gaurd.
"""

from llm_guard import scan_prompt
from llm_guard.input_scanners import PromptInjection, Secrets, TokenLimit


SECURITY_SCANNERS = [
    TokenLimit(limit=2000),          # Checks tokens
    PromptInjection(threshold=0.5),  # Defend against prompt injection attacks
    Secrets(),                        # Catches secrets like passwords and API keys
]

def validator_node(state: dict) -> dict:
    log = "[Validator] Checking input structure and security..."
    print(log)

    raw = state.get("user_requirements", "")

    try:
        sanitized_text, results_valid, results_score = scan_prompt(raw, SECURITY_SCANNERS)

        if not all(results_valid.values()):
            raise ValueError(f"Security threat detected (scores: {results_score})")

        approved_log = "[Validator] Input approved and sanitized."
        print(approved_log)
        
        return {
            "user_requirements": sanitized_text,
            "current_agent": "validator",
            "agent_logs": [log, approved_log],
        }

    except ValueError as e:
        rejected_log = f"[Validator] Rejected: {str(e)}"
        print(rejected_log)
        return {
            "user_requirements": raw,
            "current_agent": "validator",
            "status": "rejected",
            "error_messages": [str(e)],
            "agent_logs": [log, rejected_log],
        }


def route_after_validator(state: dict) -> str:
    return "rejected" if state.get("status") == "rejected" else "architect"