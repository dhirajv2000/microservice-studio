"""
Entry point. Runs the Streamlit UI.
"""

import os
import subprocess
import sys


# Strip Streamlit-specific env vars so they don't override our CLI flags
clean_env = {
    k: v for k, v in os.environ.items()
    if k not in ("STREAMLIT_SERVER_PORT", "STREAMLIT_SERVER_ADDRESS")
}

port = os.environ.get("PORT", "8501")  # honour platform-provided PORT if set

print(f"Starting Streamlit on 0.0.0.0:{port}", flush=True)

result = subprocess.run(
    [
        sys.executable, "-m", "streamlit", "run", "ui/app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
    ],
    env=clean_env,
)

sys.exit(result.returncode)
