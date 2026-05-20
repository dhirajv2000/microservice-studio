"""
Developer agent Reads the Architect's structured plan and the skeleton templates, writes
models.py and main.py.
"""

from dotenv import load_dotenv
import os

from agents.architect import render_plan_for_developer
load_dotenv()
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from schemas.developer import DeveloperOutput


llm = ChatAnthropic(model=os.getenv('ANTHROPIC_MODEL'), temperature=0)
structured_llm = llm.with_structured_output(DeveloperOutput).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

with open("template/models.py", "r") as f:
    MODELS_SKELETON = f.read()

with open("template/main.py", "r") as f:
    MAIN_SKELETON = f.read()


SYSTEM_PROMPT = """You are a senior FastAPI developer. Fill in the provided skeleton files.

        Rules for models.py:
        - Only write SQLAlchemy model classes
        - Every model inherits from Base
        - Every model has id = Column(Integer, primary_key=True, index=True)
        - Do NOT add new imports

        Rules for main.py:
        - Write Pydantic schemas in the schemas section
        - Every {Resource}Out schema must have model_config = ConfigDict(from_attributes=True)
        - Every {Resource}Update schema must have all Optional fields
        - List endpoints must have skip: int = Query(0, ge=0) and limit: int = Query(20, ge=1, le=100)
        - Use HTTPException(status_code=404) for missing resources
        - Use func.count(), func.avg(), func.sum() for aggregations
        - Do NOT add new imports

        CRITICAL ROUTE ORDERING RULE — this is the most common bug, do not make this mistake:
        FastAPI matches routes top to bottom. A parametric route like /todos/{id} will match
        ANY path including /todos/stats, treating "stats" as the id value.

        You MUST always define routes in this exact order:
        1. GET  /resource          (list)
        2. POST /resource          (create)
        3. GET  /resource/stats    (aggregations) ← MUST be before /{id}
        4. GET  /resource/{id}     (get one)
        5. PUT  /resource/{id}     (update)
        6. DELETE /resource/{id}   (delete)

        If you put /{id} before /stats the stats endpoint will NEVER work.

        SECURITY RULES — your code will be reviewed by a security agent:
        - Never use os.system, subprocess, eval, exec, or __import__
        - Never make outbound network calls (requests, urllib, httpx, socket)
        - Never hardcode credentials, API keys, or tokens
        - Use SQLAlchemy ORM only — no raw SQL string formatting"""


def developer_agent(state: dict) -> dict:
    retry_num = state.get("qa_retries", 0) + state.get("critic_retries", 0)
    log = f"[Developer] {'Writing' if retry_num == 0 else 'Revising'} code (attempt {retry_num + 1})..."
    print(log)

    # Render the structured plan into a deterministic text block
    plan_text = render_plan_for_developer(state["architecture_plan"])

    # Consolidate feedback from previous attempt (security and/or QA)
    feedback_parts: list[str] = []
    if state.get("security_feedback"):
        feedback_parts.append(f"Security issues to fix:\n{state['security_feedback']}")
    if state.get("qa_output") and state.get("qa_results") == "fail":
        feedback_parts.append(f"QA test failures to fix:\n{state['qa_output']}")
    feedback = ""
    if feedback_parts:
        feedback = " FEEDBACK FROM PREVIOUS ATTEMPT — fix all of these: " + " ".join(feedback_parts)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""User requirements:
        {state['user_requirements']}

        Architecture plan:
        {plan_text}

        models.py skeleton:
        {MODELS_SKELETON}

        main.py skeleton:
        {MAIN_SKELETON}
        {feedback}

        Fill in both skeleton files completely."""),
    ]

    try:
        result = structured_llm.invoke(messages)
        models_content = result.models_py.strip()
        main_content = result.main_py.strip()
    except Exception as e:
        error_msg = f"[Developer] Failed: {e}"
        print(error_msg)
        return {
            "current_agent": "developer",
            "agent_logs": [log, error_msg],
            "error_messages": [error_msg],
            "status": "failed",
        }

    return {
        "models_py": models_content,
        "main_py": main_content,
        "security_approved": False,
        "security_feedback": None,
        "qa_results": "pending",
        "qa_output": None,
        "current_agent": "developer",
        "agent_logs": [log, "[Developer] models.py and main.py written."],
    }
