"""
Streamlit UI for the multi-agent FastAPI generator.

This file is AI generated to save time on UI development.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import streamlit as st
from langgraph.types import Command

from graph.graph import graph
from graph.state import initial_state
from utils.zipper import create_zip


# ─────────────────────────────────────────────────────────────────────────────
# Page config and theme
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Agent Forge — FastAPI Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
  .stApp {
    background: radial-gradient(ellipse at top, #1a1d29 0%, #0e1018 60%);
    color: #e4e6eb;
  }
  #MainMenu, footer, header { visibility: hidden; }

  .forge-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #7c3aed 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.1rem;
  }
  .forge-subtitle {
    color: #9aa0aa;
    font-size: 0.95rem;
    margin-bottom: 1.8rem;
  }

  .panel-title {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b7280;
    margin-bottom: 0.6rem;
  }

  .agent-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
  .chip {
    padding: 0.32rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    border: 1px solid;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }
  .chip-pending  { background: rgba(255,255,255,0.02); border-color: rgba(255,255,255,0.1); color: #6b7280; }
  .chip-active   { background: rgba(124, 58, 237, 0.15); border-color: #7c3aed; color: #c4b5fd; animation: pulse 1.4s ease-in-out infinite; }
  .chip-done     { background: rgba(16, 185, 129, 0.12); border-color: rgba(16, 185, 129, 0.5); color: #6ee7b7; }
  .chip-failed   { background: rgba(239, 68, 68, 0.12);  border-color: rgba(239, 68, 68, 0.5);  color: #fca5a5; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.55; } }

  .terminal {
    background: #07090f;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
    font-size: 0.82rem;
    color: #c0c4cf;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.55;
  }
  .terminal .line-ok    { color: #6ee7b7; }
  .terminal .line-fail  { color: #fca5a5; }
  .terminal .line-info  { color: #93c5fd; }

  .banner {
    padding: 0.9rem 1.2rem;
    border-radius: 10px;
    font-weight: 500;
    margin-bottom: 1rem;
    border: 1px solid;
  }
  .banner-ok   { background: rgba(16,185,129,0.08);  border-color: rgba(16,185,129,0.4); color: #6ee7b7; }
  .banner-fail { background: rgba(239,68,68,0.08);   border-color: rgba(239,68,68,0.4);  color: #fca5a5; }
  .banner-warn { background: rgba(245,158,11,0.08);  border-color: rgba(245,158,11,0.4); color: #fcd34d; }

  .stButton > button {
    background: linear-gradient(90deg, #7c3aed 0%, #06b6d4 100%);
    color: white;
    border: 0;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
    transition: transform 0.1s ease;
  }
  .stButton > button:hover { transform: translateY(-1px); }

  .stTextArea textarea {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    color: #e4e6eb;
    border-radius: 8px;
    font-family: inherit;
  }

  .stTabs [data-baseweb="tab-list"] { gap: 0.4rem; }
  .stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.03);
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1rem;
  }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

if "result"        not in st.session_state: st.session_state.result        = None
if "thread_id"     not in st.session_state: st.session_state.thread_id     = None
if "status"        not in st.session_state: st.session_state.status        = None

if "pending_input" not in st.session_state: st.session_state.pending_input = None
if "pending_kind"  not in st.session_state: st.session_state.pending_kind  = None


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="forge-title">⚡ Agent Forge</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="forge-subtitle">'
    'A multi-agent system that designs, writes, security-reviews, tests, '
    'and packages a FastAPI backend from a one-line spec.'
    '</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

AGENT_PIPELINE = [
    ("validator",  "Validator"),
    ("architect",  "Architect"),
    ("developer",  "Developer"),
    ("security",   "Security"),
    ("qa",         "QA"),
    ("dockerize",  "Dockerize"),
]


def completed_agents_from_logs(logs):
    completed = set()
    log_text = " ".join(logs).lower()
    if "[validator] ✅" in log_text:  completed.add("validator")
    if "[architect] ✅" in log_text:  completed.add("architect")
    if "[developer] ✅" in log_text:  completed.add("developer")
    if "[security] ✅" in log_text:   completed.add("security")
    if "[qa] ✅" in log_text:         completed.add("qa")
    if "[dockerize] ✅" in log_text:  completed.add("dockerize")
    return completed


def render_timeline(current, status, completed):
    chips = []
    terminal = status in ("success", "rejected", "needs_human", "failed", "accepted_partial")
    for key, label in AGENT_PIPELINE:
        if key in completed:
            cls, icon = "chip-done", "✓"
        elif key == current and not terminal:
            cls, icon = "chip-active", "●"
        elif status == "failed" and key == current:
            cls, icon = "chip-failed", "✕"
        else:
            cls, icon = "chip-pending", "○"
        chips.append(f'<span class="chip {cls}">{icon} {label}</span>')
    return f'<div class="agent-row">{"".join(chips)}</div>'


def render_log(logs):
    out = []
    for line in logs:
        css_class = "line-info"
        if "✅" in line or "approved" in line.lower() or "passed" in line.lower():
            css_class = "line-ok"
        elif "❌" in line or "failed" in line.lower() or "rejected" in line.lower():
            css_class = "line-fail"
        out.append(f'<span class="{css_class}">{line}</span>')
    return '<div class="terminal">' + "\n".join(out) + '</div>'


def show_timeline_panel(current, status, logs):
    st.markdown('<div class="panel-title">Pipeline status</div>', unsafe_allow_html=True)
    st.markdown(
        render_timeline(current, status, completed_agents_from_logs(logs)),
        unsafe_allow_html=True,
    )


def show_logs_panel(logs):
    if not logs:
        return
    st.markdown('<div class="panel-title">Agent log</div>', unsafe_allow_html=True)
    st.markdown(render_log(logs), unsafe_allow_html=True)


def security_failed(result):
    return result.get("security_approved") is False and bool(result.get("security_feedback"))


def qa_failed(result):
    return result.get("qa_results") == "fail"


# ─────────────────────────────────────────────────────────────────────────────
# Input panel
# ─────────────────────────────────────────────────────────────────────────────

col_input, col_meta = st.columns([3, 1])

with col_input:
    st.markdown('<div class="panel-title">Describe your API</div>', unsafe_allow_html=True)
    requirements = st.text_area(
        "input",
        placeholder=(
            "e.g. Build a train arrival log system. Each log records a train ID, "
            "station name, scheduled arrival time, actual arrival time, and delay "
            "in minutes. CRUD endpoints plus a stats endpoint with average delay."
        ),
        height=140,
        label_visibility="collapsed",
    )
    generate = st.button("🚀 Forge it", use_container_width=False)

with col_meta:
    st.markdown('<div class="panel-title">Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#9aa0aa; font-size:0.85rem; line-height:1.7;">'
        'Validator → Architect → Developer → (Security ∥ QA) → Dockerize'
        '<br><br>'
        '<span style="color:#6b7280; font-size:0.75rem;">'
        'Security &amp; QA run in parallel as independent verifiers. '
        'Failures route back to Developer with consolidated feedback.'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# "Forge it" click: stage a new run
# ─────────────────────────────────────────────────────────────────────────────

if generate and requirements.strip():
    st.session_state.thread_id     = str(uuid.uuid4())
    st.session_state.result        = None
    st.session_state.status        = "running"
    st.session_state.pending_input = initial_state(requirements)
    st.session_state.pending_kind  = "new"
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Top-level streaming handler
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.pending_input is not None and st.session_state.thread_id:
    stream_input = st.session_state.pending_input
    kind         = st.session_state.pending_kind
    config       = {"configurable": {"thread_id": st.session_state.thread_id}}

    st.session_state.pending_input = None
    st.session_state.pending_kind  = None

    if kind == "resume":
        st.markdown(
            '<div class="banner banner-warn">🔄 Resuming the pipeline with your clarification…</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="panel-title" style="margin-top:1rem;">Live pipeline</div>',
        unsafe_allow_html=True,
    )
    timeline_box = st.empty()
    log_box      = st.empty()

    timeline_box.markdown(
        render_timeline("validator", "running", set()),
        unsafe_allow_html=True,
    )

    logs = []
    last_agent = ""

    for event in graph.stream(stream_input, config=config, stream_mode="updates"):
        for node, node_state in event.items():
            if node in ("__start__", "increment_retry", "verifier_join"):
                continue
            if not isinstance(node_state, dict):
                continue

            new_logs = node_state.get("agent_logs", [])
            for line in new_logs:
                if line not in logs:
                    logs.append(line)

            current_agent = node_state.get("current_agent") or last_agent
            last_agent    = current_agent or last_agent
            run_status    = node_state.get("status") or "running"
            done_set      = completed_agents_from_logs(logs)

            timeline_box.markdown(
                render_timeline(current_agent, run_status, done_set),
                unsafe_allow_html=True,
            )
            log_box.markdown(render_log(logs), unsafe_allow_html=True)

    snapshot = graph.get_state(config)
    final    = snapshot.values
    if snapshot.next:
        new_status = "needs_human"
    else:
        new_status = final.get("status") or "failed"

    timeline_box.markdown(
        render_timeline("", new_status, completed_agents_from_logs(final.get("agent_logs", logs))),
        unsafe_allow_html=True,
    )

    st.session_state.result = final
    st.session_state.status = new_status
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Result panels
# ─────────────────────────────────────────────────────────────────────────────

status = st.session_state.status
result = st.session_state.result

# ── Success ──────────────────────────────────────────────────────────────────
if status == "success" and result:
    st.markdown(
        '<div class="banner banner-ok">✅ Generation complete. Security passed, all tests green, Dockerfile ready.</div>',
        unsafe_allow_html=True,
    )

    show_timeline_panel("", status, result.get("agent_logs", []))

    zip_buf = create_zip(result)
    st.download_button(
        label="📦 Download project zip",
        data=zip_buf,
        file_name="generated_api.zip",
        mime="application/zip",
    )

    tabs = st.tabs(["main.py", "models.py", "Dockerfile", "tests"])
    with tabs[0]: st.code(result.get("main_py", ""), language="python")
    with tabs[1]: st.code(result.get("models_py", ""), language="python")
    with tabs[2]: st.code(result.get("dockerfile", ""), language="dockerfile")
    with tabs[3]: st.code(result.get("test_cases", "# no tests stored"), language="python")

    with st.expander("Show agent log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

# ── Rejected at validator ────────────────────────────────────────────────────
elif status == "rejected" and result:
    reasons = result.get("error_messages") or ["Input did not pass validation."]
    st.markdown(
        f'<div class="banner banner-fail">❌ Input rejected by validator: {reasons[-1]}</div>',
        unsafe_allow_html=True,
    )
    show_logs_panel(result.get("agent_logs", []))

# ── Human review needed ──────────────────────────────────────────────────────
elif status == "needs_human" and result:
    sec_bad = security_failed(result)
    qa_bad  = qa_failed(result)
    if sec_bad and qa_bad:
        which = "Security and QA both flagged issues"
    elif sec_bad:
        which = "Security flagged issues"
    elif qa_bad:
        which = "QA tests failed"
    else:
        which = "Verification incomplete"

    attempt = result.get("human_review_count", 0)
    attempt_suffix = f" (review attempt {attempt + 1})" if attempt > 0 else ""

    st.markdown(
        f'<div class="banner banner-warn">⚠️ {which} after the retry budget was exhausted.{attempt_suffix} Choose how to proceed.</div>',
        unsafe_allow_html=True,
    )

    show_timeline_panel("", status, result.get("agent_logs", []))

    st.markdown(
        '<div class="panel-title" style="margin-top:1.2rem;">Your call</div>',
        unsafe_allow_html=True,
    )
    new_req = st.text_area(
        "clarify",
        height=90,
        label_visibility="collapsed",
        placeholder="Optionally clarify or simplify your requirements, then click Retry...",
        key=f"hitl_clarify_{attempt}",
    )
    c1, c2 = st.columns(2)
    retry_clicked  = c1.button("🔄 Retry with clarification", use_container_width=True, key=f"hitl_retry_{attempt}")
    accept_clicked = c2.button("✅ Accept what we have",       use_container_width=True, key=f"hitl_accept_{attempt}")

    st.markdown(
        '<div class="panel-title" style="margin-top:1.2rem;">What failed</div>',
        unsafe_allow_html=True,
    )
    col_left, col_right = st.columns(2)
    with col_left:
        if sec_bad:
            st.markdown("**Security findings:**")
            st.code(result.get("security_feedback") or "(no detail)", language="text")
        if qa_bad:
            st.markdown("**QA output:**")
            st.code(result.get("qa_output") or "(no detail)", language="text")
        if not sec_bad and not qa_bad:
            st.markdown("*(no verifier-level detail available)*")
    with col_right:
        st.markdown("**Last generated main.py**")
        st.code(result.get("main_py", "") or "(empty)", language="python")

    if retry_clicked:
        clarified = new_req.strip() or result.get("user_requirements", "")
        st.session_state.status        = "running"
        st.session_state.pending_input = Command(
            resume={"action": "retry", "clarified_requirements": clarified}
        )
        st.session_state.pending_kind  = "resume"
        st.rerun()

    if accept_clicked:
        st.session_state.status        = "running"
        st.session_state.pending_input = Command(resume={"action": "accept"})
        st.session_state.pending_kind  = "resume"
        st.rerun()

# ── Accepted partial output ─────────────────────────────────────────────────
elif status == "accepted_partial" and result:
    st.markdown(
        '<div class="banner banner-warn">⚠️ Accepted partial output. The code did not pass all verifiers — review before using.</div>',
        unsafe_allow_html=True,
    )

    show_timeline_panel("", status, result.get("agent_logs", []))

    if result.get("main_py") and result.get("models_py"):
        # Dockerfile may be missing on the partial path; synthesize a minimal one so create_zip works
        if not result.get("dockerfile"):
            result["dockerfile"] = ""
        if not result.get("test_cases"):
            result["test_cases"] = "# tests were not finalized"
        zip_buf = create_zip(result)
        st.download_button(
            label="📦 Download partial project zip",
            data=zip_buf,
            file_name="generated_api_partial.zip",
            mime="application/zip",
        )

    tabs = st.tabs(["main.py", "models.py", "tests", "What failed"])
    with tabs[0]: st.code(result.get("main_py", "") or "(empty)", language="python")
    with tabs[1]: st.code(result.get("models_py", "") or "(empty)", language="python")
    with tabs[2]: st.code(result.get("test_cases", "") or "# no tests stored", language="python")
    with tabs[3]:
        if security_failed(result):
            st.markdown("**Security findings:**")
            st.code(result.get("security_feedback") or "(no detail)", language="text")
        if qa_failed(result):
            st.markdown("**QA output:**")
            st.code(result.get("qa_output") or "(no detail)", language="text")

    with st.expander("Show agent log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

# ── Failed (architect or developer LLM error) ───────────────────────────────
elif status == "failed":
    msg = "Generation failed."
    if result and result.get("error_messages"):
        msg = result["error_messages"][-1]
    st.markdown(
        f'<div class="banner banner-fail">❌ {msg}</div>',
        unsafe_allow_html=True,
    )
    if result:
        show_logs_panel(result.get("agent_logs", []))