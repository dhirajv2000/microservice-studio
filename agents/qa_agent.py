"""
QA agent generates test cases and tests the code in a sub process environment.
"""

import os
import ast
import subprocess
import tempfile
import threading
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware
from langchain_core.tools import tool

from schemas.qa import QAVerdict


with open("template/database.py") as f:
    DATABASE_PY = f.read()

with open("template/conftest.py") as f:
    CONFTEST = f.read()


_qa_code_lock = threading.Lock()
_qa_code_by_thread: dict[int, dict] = {}


@tool
def run_tests(test_code: str) -> dict[str, Any]:
    """
    Run the provided pytest test code against the current generated FastAPI app.

    The test environment provides a `client` fixture (FastAPI TestClient) and
    auto-creates/drops database tables around each test. Tests should use the
    fixture: def test_something(client): ...

    Returns:
        {"passed": bool, "output": str, "syntax_ok": bool}
    """
    try:
        ast.parse(test_code)
    except SyntaxError as e:
        return {"passed": False, "output": f"Test code has a syntax error: {e}", "syntax_ok": False}

    with _qa_code_lock:
        ident = threading.get_ident()
        code = _qa_code_by_thread.get(ident)
        if code is None and _qa_code_by_thread:
            # Use the most recently written entry.
            code = list(_qa_code_by_thread.values())[-1]
    models_py = code["models_py"] if code else ""
    main_py   = code["main_py"]   if code else ""

    if not models_py or not main_py:
        return {
            "passed": False,
            "output": "QA tool could not locate the generated code (models.py or main.py was empty).",
            "syntax_ok": True,
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        files = {
            "database.py":  DATABASE_PY,
            "models.py":    models_py,
            "main.py":      main_py,
            "test_main.py": test_code,
            "conftest.py":  CONFTEST,
        }
        for name, content in files.items():
            with open(os.path.join(tmpdir, name), "w") as f:
                f.write(content)

        result = subprocess.run(
            ["python", "-m", "pytest", "test_main.py", "-v", "--tb=short"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "DATABASE_URL": f"sqlite:///{tmpdir}/test.db"},
        )
        return {
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "syntax_ok": True,
        }


SYSTEM_PROMPT = """You are a QA engineer testing a generated FastAPI app.

Workflow:
1. Read the user message containing main.py.
2. Write pytest tests covering every endpoint.
3. Call run_tests(test_code=...) ONCE with your tests.
4. Read the result. If passed=true, return your verdict. If passed=false, you
   may revise the tests ONCE and call run_tests again. Do not loop more than that.
5. Return your verdict with the final test code.

Test rules:
- Use the `client` fixture in every test: def test_something(client): ...
- Do NOT create TestClient yourself — use the fixture.
- Do NOT call Base.metadata.create_all — the conftest handles it.
- Test every endpoint. For each endpoint test success AND a 404 case where applicable.
- Create test data inside each test using POST requests.
- No async tests.
- Only `import pytest` at the top — the conftest provides everything else.

Be efficient: write good tests the first time so you only need one run_tests call."""

qa_agent_runtime = create_agent(
    model=f"anthropic:{os.getenv('ANTHROPIC_MODEL')}",
    tools=[run_tests],
    system_prompt=SYSTEM_PROMPT,
    response_format=QAVerdict,
    middleware=[
        ModelRetryMiddleware(max_retries=2),
    ],
)


# ── Node ──────────────────────────────────────────────────────────────────────

def qa_node(state: dict) -> dict:
    start_log     = "[QA] Generating pytest test cases..."
    sandbox_log   = "[QA] Spinning up sandbox and installing dependencies..."
    run_log       = "[QA] Running pytest against generated app..."
    print(start_log)
    print(sandbox_log)
    print(run_log)

    # Stash this run's code keyed by the current thread.
    with _qa_code_lock:
        _qa_code_by_thread[threading.get_ident()] = {
            "models_py": state["models_py"],
            "main_py":   state["main_py"],
        }

    user_message = f"""Write and run pytest tests for this FastAPI app.

main.py:
```python
{state['main_py']}
```

Write tests covering every endpoint, then call run_tests to verify them."""

    try:
        result = qa_agent_runtime.invoke({
            "messages": [{"role": "user", "content": user_message}],
        })
        verdict: QAVerdict = result["structured_response"]
        passed = verdict.passed
        test_code = verdict.test_code
        summary = verdict.summary
    except Exception as e:
        error_msg = f"[QA] Agent failed: {e}"
        print(error_msg)
        return {
            "qa_results": "fail",
            "qa_output": f"QA agent could not complete: {e}",
            "test_cases": "",
            "agent_logs": [start_log, sandbox_log, run_log, error_msg],
            "error_messages": [error_msg],
        }

    if passed:
        result_log = f"[QA] All tests passed — {summary}"
    else:
        result_log = f"[QA] Tests failed — {summary}"
    print(result_log)

    return {
        "qa_results": "pass" if passed else "fail",
        "qa_output": summary,
        "test_cases": test_code,
        "agent_logs": [start_log, sandbox_log, run_log, result_log],
        "error_messages": [summary] if not passed else [],
    }