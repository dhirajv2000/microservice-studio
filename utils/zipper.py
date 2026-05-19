import io
import zipfile


def create_zip(state: dict) -> io.BytesIO:
    """
    Creates a zip file from the agent state.
    Returns a BytesIO buffer ready for Streamlit download_button.
    """
    with open("template/database.py") as f:
        database_py = f.read()

    with open("template/requirements.txt") as f:
        requirements_txt = f.read()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("main.py",            state["main_py"])
        zf.writestr("models.py",          state["models_py"])
        zf.writestr("database.py",        database_py)
        zf.writestr("requirements.txt",   requirements_txt)
        zf.writestr("tests/test_main.py", state["test_cases"])
        zf.writestr("Dockerfile",         state["dockerfile"])

    buf.seek(0)
    return buf