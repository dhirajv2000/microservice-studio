import operator
from typing import TypedDict, Annotated, List


class AgentState(TypedDict):
    # Input
    user_requirements: str

    # State for logging and UI 
    current_agent: str
    agent_logs:    Annotated[List[str], operator.add]

    # Gives Status
    status:         str
    error_messages: Annotated[List[str], operator.add]


def initial_state(user_requirements: str) -> AgentState:
    return AgentState(
        user_requirements=user_requirements,

        current_agent="",
        agent_logs=[],

        status="running",
        error_messages=[],
    )