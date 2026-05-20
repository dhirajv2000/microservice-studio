import operator
from typing import TypedDict, Annotated, List, Optional

class AgentState(TypedDict):
    # Input
    user_requirements: str

    # Serialised ArchitecturePlan produced by the architect agent
    architecture_plan: Optional[dict]

    # Generated file contents written by the developer agent
    models_py: Optional[str]
    main_py:   Optional[str]

    # Security critic verdict
    security_approved: bool
    security_feedback: Optional[str]

    # QA verdict
    qa_results: str            # "pass" | "fail" | "pending"
    qa_output:  Optional[str]
    test_cases: Optional[str]

    # Dockerfile produced by the dockerize node
    dockerfile: Optional[str]

    # Loop control
    retries:     int
    max_retries: int
    human_review_count: int

    # State for logging and UI
    current_agent: str
    agent_logs:    Annotated[List[str], operator.add]

    # Gives Status
    status:         str
    error_messages: Annotated[List[str], operator.add]


def initial_state(user_requirements: str) -> AgentState:
    return AgentState(
        user_requirements=user_requirements,

        architecture_plan=None,

        models_py=None,
        main_py=None,

        security_approved=False,
        security_feedback=None,

        qa_results="pending",
        qa_output=None,
        test_cases=None,

        dockerfile=None,

        retries=0,
        max_retries=2,
        human_review_count=0,

        current_agent="",
        agent_logs=[],

        status="running",
        error_messages=[],
    )