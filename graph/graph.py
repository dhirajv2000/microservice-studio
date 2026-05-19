from langgraph.graph import END, START, StateGraph

from agents.architect import architect_agent
from agents.developer import developer_agent
from agents.docker_node import dockerize_node
from agents.qa_agent import qa_node
from agents.security_critic import security_critic_node
from agents.validator_node import validator_node
from graph.state import AgentState
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

#Human in the loop flow
def human_review(state: AgentState) -> dict:
    decision = interrupt({
        "message": "Two attempts failed verification.",
        "failures": state.get("error_messages", []),
        "last_main_py": state.get("main_py", ""),
        "security_feedback": state.get("security_feedback"),
        "qa_output": state.get("qa_output"),
    })

    if decision.get("action") == "retry":
        return {
            "user_requirements": decision.get(
                "clarified_requirements", state["user_requirements"]
            ),
            "retries": 0,
            "status": "running",
            "agent_logs": ["[Human] User clarified requirements and retried."],
        }

    return {
        "status": "needs_human",
        "agent_logs": ["[Human] User accepted partial output."],
    }

#Node that just increments retry count
def increment_retry(state: AgentState) -> dict:
    return {"retries": state.get("retries", 0) + 1}

#Place holder node to handle flow after parallel nodes run
def verifier_join(state: AgentState) -> dict:
    return {}

def route_after_verifiers(state: AgentState) -> str:
    sec_ok = state.get("security_approved", False)
    qa_ok  = state.get("qa_results") == "pass"

    if sec_ok and qa_ok:
        return "dockerize"

    if state.get("retries", 0) >= state.get("max_retries", 3) - 1:
        return "human_review"

    return "increment_retry"

def route_after_human(state: AgentState) -> str:
    return "architect" if state.get("status") == "running" else END

def build_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("validator",       validator_node)
    builder.add_node("architect",       architect_agent)
    builder.add_node("developer",       developer_agent)
    builder.add_node("security",        security_critic_node)
    builder.add_node("qa",              qa_node)
    builder.add_node("verifier_join",   verifier_join)
    builder.add_node("increment_retry", increment_retry)
    builder.add_node("dockerize",       dockerize_node)
    builder.add_node("human_review",    human_review)
    
    
    builder.add_edge(START, "validator")
    
    builder.add_conditional_edges(
    "validator",
    lambda state: "rejected" if state.get("status") == "rejected" else "architect",
    {"architect": "architect", "rejected": END})
    
    builder.add_edge("architect", "developer")

    builder.add_edge("developer", "security")
    builder.add_edge("developer", "qa")
    
    
    builder.add_edge("security", "verifier_join")
    builder.add_edge("qa",       "verifier_join")
    builder.add_conditional_edges(
    "verifier_join",
    route_after_verifiers,
    {
        "dockerize":       "dockerize",
        "increment_retry": "increment_retry",
        "human_review":    "human_review",
    })
    
    builder.add_edge("increment_retry", "developer")
    
    
    builder.add_conditional_edges(
    "human_review",
    route_after_human,
    {"architect": "architect", END: END})
    
    builder.add_edge("dockerize", END)
    
    
    return builder.compile(checkpointer=MemorySaver())


graph = build_graph()