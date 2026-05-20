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
    page_title="Microservice Studio — FastAPI Generator",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
  .stApp {
    background: #0b1020;
    color: #e2e8f0;
  }
  .block-container { padding-top: 2.4rem; max-width: 1100px; }
  #MainMenu, footer, header { visibility: hidden; }

  .ms-title {
    font-size: 1.9rem;
    font-weight: 600;
    color: #f1f5f9;
    letter-spacing: -0.015em;
    margin: 0 0 0.25rem 0;
  }
  .ms-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 2rem;
  }

  .section-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    margin: 1.6rem 0 0.6rem 0;
  }
  .section-label:first-of-type { margin-top: 0.5rem; }

  /* Pipeline chips */
  .agent-row { display: flex; gap: 0.45rem; flex-wrap: wrap; }
  .chip {
    padding: 0.32rem 0.78rem;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 500;
    border: 1px solid;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Inter', -apple-system, sans-serif;
  }
  .chip-pending  { background: rgba(148, 163, 184, 0.05); border-color: rgba(148, 163, 184, 0.15); color: #64748b; }
  .chip-active   { background: rgba(59, 130, 246, 0.12);  border-color: rgba(59, 130, 246, 0.5);  color: #93c5fd; }
  .chip-done     { background: rgba(34, 197, 94, 0.10);   border-color: rgba(34, 197, 94, 0.4);   color: #86efac; }
  .chip-failed   { background: rgba(239, 68, 68, 0.10);   border-color: rgba(239, 68, 68, 0.45);  color: #fca5a5; }

  .chip-active .dot {
    width: 0.5rem; height: 0.5rem; border-radius: 50%;
    background: #60a5fa;
    animation: pulse 1.3s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }

  /* Terminal */
  .terminal {
    background: #060912;
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    font-family: ui-monospace, 'SF Mono', 'Menlo', monospace;
    font-size: 0.8rem;
    color: #cbd5e1;
    max-height: 340px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.6;
  }
  .terminal .line-ok    { color: #86efac; }
  .terminal .line-fail  { color: #fca5a5; }
  .terminal .line-info  { color: #93c5fd; }
  .terminal .line-step  { color: #cbd5e1; }

  /* Plan card */
  .plan-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 8px;
    padding: 1rem 1.2rem;
  }
  .plan-card h4 {
    color: #f1f5f9;
    margin: 0 0 0.15rem 0;
    font-size: 0.95rem;
    font-weight: 600;
  }
  .plan-sub {
    color: #64748b;
    font-size: 0.78rem;
    margin-bottom: 0.9rem;
  }
  .plan-section {
    color: #64748b;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin: 0.7rem 0 0.35rem 0;
  }
  .plan-list { margin: 0; padding-left: 1.1rem; color: #cbd5e1; font-size: 0.85rem; line-height: 1.7; }
  .plan-list li { margin-bottom: 0.1rem; }
  .plan-list.no-bullets { list-style: none; padding-left: 0; }
  .plan-meta { color: #64748b; font-size: 0.78rem; }

  .plan-method {
    display: inline-block;
    min-width: 3.2rem;
    padding: 0.05rem 0.45rem;
    border-radius: 4px;
    font-family: ui-monospace, 'SF Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    text-align: center;
    margin-right: 0.5rem;
  }
  .method-GET    { background: rgba(59, 130, 246, 0.18); color: #93c5fd; }
  .method-POST   { background: rgba(34, 197, 94, 0.18);  color: #86efac; }
  .method-PUT    { background: rgba(234, 179, 8, 0.18);  color: #fde047; }
  .method-DELETE { background: rgba(239, 68, 68, 0.18);  color: #fca5a5; }

  /* Banners */
  .banner {
    padding: 0.85rem 1.15rem;
    border-radius: 8px;
    font-size: 0.92rem;
    font-weight: 500;
    margin-bottom: 1rem;
    border: 1px solid;
  }
  .banner-ok   { background: rgba(34, 197, 94, 0.07); border-color: rgba(34, 197, 94, 0.35); color: #86efac; }
  .banner-fail { background: rgba(239, 68, 68, 0.07); border-color: rgba(239, 68, 68, 0.35); color: #fca5a5; }
  .banner-warn { background: rgba(234, 179, 8, 0.07); border-color: rgba(234, 179, 8, 0.35); color: #fde047; }

  /* Buttons */
  .stButton > button {
    background: #2563eb;
    color: white;
    border: 0;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.55rem 1.3rem;
    transition: background 0.15s ease;
  }
  .stButton > button:hover { background: #1d4ed8; }
  .stButton > button:focus { box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.35); }

  .stDownloadButton > button {
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    border: 1px solid rgba(34, 197, 94, 0.4);
    border-radius: 6px;
    font-weight: 500;
    padding: 0.55rem 1.3rem;
  }
  .stDownloadButton > button:hover {
    background: rgba(34, 197, 94, 0.22);
  }

  /* Inputs */
  .stTextArea textarea {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    color: #e2e8f0;
    border-radius: 6px;
    font-family: inherit;
    font-size: 0.92rem;
  }
  .stTextArea textarea:focus {
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.3);
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0.2rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    padding: 0.55rem 1rem;
    color: #94a3b8;
    font-size: 0.88rem;
  }
  .stTabs [aria-selected="true"] {
    color: #f1f5f9;
    border-bottom: 2px solid #3b82f6;
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

st.markdown('<div class="ms-title">Microservice Studio</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ms-subtitle">'
    'Describe a microservice. Get a security-reviewed, tested, dockerized FastAPI backend.'
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

NODE_TO_CHIP = {
    "validator": "validator",
    "architect": "architect",
    "developer": "developer",
    "security":  "security",
    "qa":        "qa",
    "dockerize": "dockerize",
}


def completed_agents_from_logs(logs):
    completed = set()
    log_text = " ".join(logs).lower()
    if "[validator] ✅" in log_text:  completed.add("validator")
    if "[architect] ✅" in log_text:  completed.add("architect")
    if "[developer] ✅" in log_text or "[developer] models.py and main.py written" in log_text:
        completed.add("developer")
    if "[security] ✅" in log_text:   completed.add("security")
    if "[qa] ✅" in log_text:         completed.add("qa")
    if "[dockerize] ✅" in log_text:  completed.add("dockerize")
    return completed


def render_timeline(active_set, status, completed):
    """active_set is a set of chip keys currently running."""
    chips = []
    terminal = status in ("success", "rejected", "needs_human", "failed", "accepted_partial")
    for key, label in AGENT_PIPELINE:
        if key in completed:
            cls, icon = "chip-done", "✓"
            chips.append(f'<span class="chip {cls}">{icon} {label}</span>')
        elif key in active_set and not terminal:
            chips.append(f'<span class="chip chip-active"><span class="dot"></span>{label}</span>')
        elif status == "failed" and key in active_set:
            chips.append(f'<span class="chip chip-failed">✕ {label}</span>')
        else:
            chips.append(f'<span class="chip chip-pending">○ {label}</span>')
    return f'<div class="agent-row">{"".join(chips)}</div>'


def render_log(logs):
    out = []
    for line in logs:
        css_class = "line-step"
        lower = line.lower()
        if "✅" in line or " approved" in lower or "passed" in lower:
            css_class = "line-ok"
        elif "❌" in line or "failed" in lower or "rejected" in lower or "error" in lower:
            css_class = "line-fail"
        elif lower.startswith("[validator]") or lower.startswith("[architect]") or lower.startswith("[developer]"):
            css_class = "line-info"
        out.append(f'<span class="{css_class}">{line}</span>')
    return '<div class="terminal">' + "\n".join(out) + '</div>'


def render_plan_card(plan_dict):
    if not plan_dict:
        return ""

    models = plan_dict.get("models", []) or []
    endpoints = plan_dict.get("endpoints", []) or []
    notes = plan_dict.get("notes", "") or ""

    parts = ['<div class="plan-card">']
    parts.append('<h4>Architecture plan</h4>')
    parts.append(
        f'<div class="plan-sub">{len(models)} model · {len(endpoints)} endpoint</div>'
    )

    if models:
        parts.append('<div class="plan-section">Models</div>')
        for m in models:
            name = m.get("name", "?")
            table = m.get("table_name", "?")
            fields = m.get("fields", []) or []
            parts.append(
                f'<div style="margin-bottom:0.4rem;">'
                f'<span style="color:#f1f5f9;font-weight:600;">{name}</span>'
                f' <span class="plan-meta">· table: {table}</span>'
                f'</div>'
            )
            parts.append('<ul class="plan-list">')
            parts.append('<li><span class="plan-meta">id: Integer (auto)</span></li>')
            for f in fields:
                fname = f.get("name", "?")
                ftype = f.get("type", "?")
                nullable = "nullable" if f.get("nullable", True) else "required"
                parts.append(f'<li>{fname}: {ftype} <span class="plan-meta">· {nullable}</span></li>')
            parts.append('</ul>')

    if endpoints:
        parts.append('<div class="plan-section">Endpoints</div>')
        parts.append('<ul class="plan-list no-bullets">')
        for e in endpoints:
            method = (e.get("method") or "GET").upper()
            path = e.get("path", "?")
            desc = e.get("description", "")
            method_class = f"method-{method}" if method in ("GET", "POST", "PUT", "DELETE") else ""
            parts.append(
                f'<li>'
                f'<span class="plan-method {method_class}">{method}</span>'
                f'<code style="color:#e2e8f0;background:transparent;">{path}</code>'
                f' <span class="plan-meta">— {desc}</span>'
                f'</li>'
            )
        parts.append('</ul>')

    if notes:
        parts.append('<div class="plan-section">Notes</div>')
        parts.append(f'<div style="color:#cbd5e1; font-size:0.85rem;">{notes}</div>')

    parts.append('</div>')
    return "".join(parts)


def show_timeline(active_set, status, logs):
    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        render_timeline(active_set, status, completed_agents_from_logs(logs)),
        unsafe_allow_html=True,
    )


def show_logs(logs):
    if not logs:
        return
    st.markdown('<div class="section-label">Agent activity</div>', unsafe_allow_html=True)
    st.markdown(render_log(logs), unsafe_allow_html=True)


def security_failed(result):
    return result.get("security_approved") is False and bool(result.get("security_feedback"))


def qa_failed(result):
    return result.get("qa_results") == "fail"


# ─────────────────────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-label">Describe your microservice</div>', unsafe_allow_html=True)
requirements = st.text_area(
    "input",
    placeholder=(
        "e.g. Build a train arrival log system. Each log records a train ID, "
        "station name, scheduled arrival time, actual arrival time, and delay "
        "in minutes. CRUD endpoints plus a stats endpoint with average delay."
    ),
    height=130,
    label_visibility="collapsed",
)
generate = st.button("Generate microservice")


# ─────────────────────────────────────────────────────────────────────────────
# Stage a new run
# ─────────────────────────────────────────────────────────────────────────────

if generate and requirements.strip():
    st.session_state.thread_id     = str(uuid.uuid4())
    st.session_state.result        = None
    st.session_state.status        = "running"
    st.session_state.pending_input = initial_state(requirements)
    st.session_state.pending_kind  = "new"
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Streaming handler
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.pending_input is not None and st.session_state.thread_id:
    stream_input = st.session_state.pending_input
    kind         = st.session_state.pending_kind
    config       = {"configurable": {"thread_id": st.session_state.thread_id}}

    st.session_state.pending_input = None
    st.session_state.pending_kind  = None

    if kind == "resume":
        st.markdown(
            '<div class="banner banner-warn">Resuming the pipeline with your clarification…</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    timeline_box = st.empty()
    plan_box     = st.empty()
    st.markdown('<div class="section-label">Agent activity</div>', unsafe_allow_html=True)
    log_box      = st.empty()

    timeline_box.markdown(
        render_timeline({"validator"}, "running", set()),
        unsafe_allow_html=True,
    )

    logs = []
    active_set = set()
    plan_rendered = False

    for event in graph.stream(stream_input, config=config, stream_mode="updates"):
        # Each event can carry multiple nodes (parallel fan-out: security + qa).
        # First pass: collect every node that yielded in this tick so chips
        # reflect what just ran, even if both finished at the same time.
        nodes_in_event = [n for n in event.keys() if n not in ("__start__", "increment_retry", "verifier_join")]

        for node in nodes_in_event:
            node_state = event[node]
            if not isinstance(node_state, dict):
                continue

            # Append any new log lines from this node.
            for line in node_state.get("agent_logs", []):
                if line not in logs:
                    logs.append(line)

            # Mark this node as having run (it finished, which is why we got
            # the event). Remove from "active" — completion comes from logs.
            chip_key = NODE_TO_CHIP.get(node)
            if chip_key:
                active_set.discard(chip_key)

            # Plan card appears as soon as architect yields.
            if node == "architect" and not plan_rendered:
                plan_dict = node_state.get("architecture_plan")
                if plan_dict:
                    plan_box.markdown(render_plan_card(plan_dict), unsafe_allow_html=True)
                    plan_rendered = True

        # Predict which nodes are about to run next based on what just finished.
        # This lets the chip light up DURING the next phase, not after.
        next_active = set()
        finished_now = {NODE_TO_CHIP.get(n) for n in nodes_in_event if NODE_TO_CHIP.get(n)}
        if "validator" in finished_now:
            next_active.add("architect")
        if "architect" in finished_now:
            next_active.add("developer")
        if "developer" in finished_now:
            # Developer fans out to security AND qa in parallel.
            next_active.update({"security", "qa"})
        if "security" in finished_now or "qa" in finished_now:
            # Wait until both finish before predicting dockerize. If only one
            # is done, keep the other one active.
            completed_so_far = completed_agents_from_logs(logs)
            if "security" not in completed_so_far:
                next_active.add("security")
            if "qa" not in completed_so_far:
                next_active.add("qa")
            if "security" in completed_so_far and "qa" in completed_so_far:
                next_active.add("dockerize")

        # Read run status from whichever node we saw last (best effort).
        run_status = "running"
        for node in nodes_in_event:
            ns = event.get(node)
            if isinstance(ns, dict) and ns.get("status"):
                run_status = ns["status"]

        done_set = completed_agents_from_logs(logs)
        # Don't show "active" for nodes already complete.
        next_active -= done_set

        timeline_box.markdown(
            render_timeline(next_active, run_status, done_set),
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
        render_timeline(set(), new_status, completed_agents_from_logs(final.get("agent_logs", logs))),
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
        '<div class="banner banner-ok">Generation complete. Security passed, tests green, Dockerfile ready.</div>',
        unsafe_allow_html=True,
    )

    show_timeline(set(), status, result.get("agent_logs", []))

    if result.get("architecture_plan"):
        st.markdown('<div class="section-label">Plan</div>', unsafe_allow_html=True)
        st.markdown(render_plan_card(result["architecture_plan"]), unsafe_allow_html=True)

    st.markdown('<div class="section-label">Output</div>', unsafe_allow_html=True)
    zip_buf = create_zip(result)
    st.download_button(
        label="Download project zip",
        data=zip_buf,
        file_name="generated_api.zip",
        mime="application/zip",
    )

    tabs = st.tabs(["main.py", "models.py", "Dockerfile", "tests"])
    with tabs[0]: st.code(result.get("main_py", ""), language="python")
    with tabs[1]: st.code(result.get("models_py", ""), language="python")
    with tabs[2]: st.code(result.get("dockerfile", ""), language="dockerfile")
    with tabs[3]: st.code(result.get("test_cases", "# no tests stored"), language="python")

    with st.expander("Agent activity log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

# ── Rejected at validator ────────────────────────────────────────────────────
elif status == "rejected" and result:
    reasons = result.get("error_messages") or ["Input did not pass validation."]
    st.markdown(
        f'<div class="banner banner-fail">Input rejected: {reasons[-1]}</div>',
        unsafe_allow_html=True,
    )
    show_logs(result.get("agent_logs", []))

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
        f'<div class="banner banner-warn">{which} after the retry budget was exhausted.{attempt_suffix} Choose how to proceed.</div>',
        unsafe_allow_html=True,
    )

    show_timeline(set(), status, result.get("agent_logs", []))

    if result.get("architecture_plan"):
        st.markdown('<div class="section-label">Plan</div>', unsafe_allow_html=True)
        st.markdown(render_plan_card(result["architecture_plan"]), unsafe_allow_html=True)

    st.markdown('<div class="section-label">Your call</div>', unsafe_allow_html=True)
    new_req = st.text_area(
        "clarify",
        height=90,
        label_visibility="collapsed",
        placeholder="Optionally clarify or simplify your requirements, then retry...",
        key=f"hitl_clarify_{attempt}",
    )
    c1, c2 = st.columns(2)
    retry_clicked  = c1.button("Retry with clarification", use_container_width=True, key=f"hitl_retry_{attempt}")
    accept_clicked = c2.button("Accept what we have",      use_container_width=True, key=f"hitl_accept_{attempt}")

    st.markdown('<div class="section-label">What failed</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        if sec_bad:
            st.markdown("**Security findings**")
            st.code(result.get("security_feedback") or "(no detail)", language="text")
        if qa_bad:
            st.markdown("**QA output**")
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
        '<div class="banner banner-warn">Accepted partial output. The code did not pass all verifiers — review before using.</div>',
        unsafe_allow_html=True,
    )

    show_timeline(set(), status, result.get("agent_logs", []))

    if result.get("architecture_plan"):
        st.markdown('<div class="section-label">Plan</div>', unsafe_allow_html=True)
        st.markdown(render_plan_card(result["architecture_plan"]), unsafe_allow_html=True)

    if result.get("main_py") and result.get("models_py"):
        if not result.get("dockerfile"):
            result["dockerfile"] = ""
        if not result.get("test_cases"):
            result["test_cases"] = "# tests were not finalized"
        zip_buf = create_zip(result)
        st.download_button(
            label="Download partial project zip",
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
            st.markdown("**Security findings**")
            st.code(result.get("security_feedback") or "(no detail)", language="text")
        if qa_failed(result):
            st.markdown("**QA output**")
            st.code(result.get("qa_output") or "(no detail)", language="text")

    with st.expander("Agent activity log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

# ── Failed ──────────────────────────────────────────────────────────────────
elif status == "failed":
    msg = "Generation failed."
    if result and result.get("error_messages"):
        msg = result["error_messages"][-1]
    st.markdown(
        f'<div class="banner banner-fail">{msg}</div>',
        unsafe_allow_html=True,
    )
    if result:
        show_logs(result.get("agent_logs", []))