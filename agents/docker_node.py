DOCKERFILE = """FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=sqlite:////app/data/app.db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""


def dockerize_node(state: dict) -> dict:
    log = "[Dockerize] ✅ Dockerfile generated."
    print(log)
    return {
        "dockerfile": DOCKERFILE.strip(),
        "current_agent": "dockerize",
        "status": "success",
        "agent_logs": [log],
    }
