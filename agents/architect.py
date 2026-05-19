"""
Architect agent is used to read the reuqiremnts and provide the developer agent with very specific plans on 
how to go about the exectution.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from schemas.architect import ArchitecturePlan

SYSTEM_PROMPT = """You are a senior software architect specialising in FastAPI + SQLAlchemy + SQLite REST APIs.

Your job is to read user requirements and produce a structured implementation plan.

The project always uses this fixed structure:
- main.py      → FastAPI app and all route definitions
- models.py    → SQLAlchemy ORM models only
- database.py  → already written, never modify

Rules:
- Only design endpoints implementable with FastAPI + SQLite. No auth, no external APIs, no background tasks, no websockets.
- Every model gets an Integer primary key called `id` automatically — do NOT include id in the fields list.
- Field types must be exactly one of: Integer, String, DateTime, Float, Boolean
- Be specific. Every endpoint must have a method, path, and one-line description.
- Keep it realistic: 1-2 models, 3-6 endpoints.
- Include a `GET /resource/stats` endpoint if aggregations would be useful (counts, averages, totals).
- Path parameters use {id}, e.g. /todos/{id}.

Output the structured plan now."""

llm = ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL"), temperature=0)
structured_llm = llm.with_structured_output(ArchitecturePlan).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)


def architect_agent(state: dict) -> dict:
    log = "[Architect] Analysing requirements..."
    print(log)

    try:
        plan: ArchitecturePlan = structured_llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"User requirements: {state['user_requirements']}  Produce the implementation plan now."),
        ])
    except Exception as e:
        error_msg = f"[Architect] Failed: {e}"
        print(error_msg)
        return {
            "current_agent": "architect",
            "agent_logs": [log, error_msg],
            "error_messages": [error_msg],
            "status": "failed",
        }

    summary = (
        f"[Architect] Plan ready: {len(plan.models)} model(s), "
        f"{len(plan.endpoints)} endpoint(s)."
    )
    print(summary)

    return {
        "architecture_plan": plan.model_dump(),
        "current_agent": "architect",
        "agent_logs": [log, summary],
    }

def render_plan_for_developer(plan_dict: dict) -> str:
    plan = ArchitecturePlan(**plan_dict)

    lines = ["## Models"]
    for m in plan.models:
        lines.append(f"\n### {m.name}  (table: {m.table_name})")
        lines.append("- id: Integer, primary key  (added automatically)")
        for f in m.fields:
            nullable_str = "nullable" if f.nullable else "NOT NULL"
            lines.append(f"- {f.name}: {f.type}  ({nullable_str})")

    lines.append("\n## Endpoints")
    for e in plan.endpoints:
        lines.append(f"- {e.method} {e.path} — {e.description}")

    if plan.notes:
        lines.append(f"\n## Notes\n{plan.notes}")

    return "\n".join(lines)