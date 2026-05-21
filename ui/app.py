"""
Streamlit UI for the multi-agent FastAPI generator.

This file is AI generated to save time on UI development.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import html as html_lib
import streamlit as st
from langgraph.types import Command

from graph.graph import graph
from graph.state import initial_state
from utils.zipper import create_zip


# ─────────────────────────────────────────────────────────────────────────────
# Page config and theme
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Microservice Studio",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  :root {
    --bg-deep:    #0a0e1f;
    --bg-panel:   #131830;
    --bg-input:   #0f1428;
    --bg-code:    #080b1c;

    --border-soft: rgba(148, 163, 200, 0.10);
    --border-mid:  rgba(148, 163, 200, 0.18);

    --text-hi:    #f5f7fb;
    --text-mid:   #c8d1e6;
    --text-low:   #8893b0;
    --text-dim:   #5b6480;

    --amber:      #f5b342;
    --amber-soft: #f5b34222;
    --coral:      #f47474;
    --coral-soft: #f4747422;
    --emerald:    #4ade80;
    --emerald-soft: #4ade8022;
    --indigo:     #818cf8;
    --indigo-soft: #818cf822;
    --sky:        #60a5fa;
    --sky-soft:   #60a5fa22;
  }

  .stApp {
    background:
      radial-gradient(ellipse 80% 50% at 50% 0%, rgba(129, 140, 248, 0.07) 0%, transparent 60%),
      var(--bg-deep);
    color: var(--text-mid);
    font-family: 'Inter', -apple-system, sans-serif;
  }
  .block-container { padding-top: 2.4rem; max-width: 1080px; }
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Header ──────────────────────────────────────────────────────────── */
  .ms-header {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 0 0 0.4rem 0;
  }
  .ms-mark {
    width: 36px; height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .ms-title {
    font-family: 'Inter Tight', sans-serif;
    font-size: 2.05rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    background: linear-gradient(135deg, #f5b342 0%, #f47474 55%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin: 0;
  }
  .ms-subtitle {
    color: var(--text-low);
    font-size: 0.96rem;
    font-weight: 400;
    margin: 0 0 2.2rem 0;
    max-width: 640px;
    line-height: 1.5;
  }

  /* ── Section labels ──────────────────────────────────────────────────── */
  .section-label {
    font-family: 'Inter Tight', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--text-dim);
    margin: 1.7rem 0 0.65rem 0;
  }
  .section-label:first-of-type { margin-top: 0.5rem; }

  /* ── Pipeline chips ──────────────────────────────────────────────────── */
  .agent-row {
    display: flex;
    gap: 0.45rem;
    flex-wrap: wrap;
    padding: 0.6rem 0;
  }
  .chip {
    font-family: 'JetBrains Mono', monospace;
    padding: 0.38rem 0.78rem;
    border-radius: 5px;
    font-size: 0.76rem;
    font-weight: 500;
    border: 1px solid;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    transition: all 0.2s ease;
  }
  .chip-pending  {
    background: rgba(148, 163, 200, 0.03);
    border-color: var(--border-soft);
    color: var(--text-dim);
  }
  .chip-active   {
    background: var(--sky-soft);
    border-color: rgba(96, 165, 250, 0.55);
    color: var(--sky);
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.08);
  }
  .chip-done     {
    background: var(--emerald-soft);
    border-color: rgba(74, 222, 128, 0.45);
    color: var(--emerald);
  }
  .chip-failed   {
    background: var(--coral-soft);
    border-color: rgba(244, 116, 116, 0.5);
    color: var(--coral);
  }

  .chip-active .dot {
    width: 0.5rem; height: 0.5rem; border-radius: 50%;
    background: var(--sky);
    box-shadow: 0 0 8px var(--sky);
    animation: pulse 1.3s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%     { opacity: 0.4; transform: scale(0.85); }
  }

  /* ── Terminal / activity log ─────────────────────────────────────────── */
  .terminal {
    background: var(--bg-code);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 1rem 1.15rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.81rem;
    color: var(--text-mid);
    max-height: 340px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.65;
  }
  .terminal .line-ok    { color: var(--emerald); }
  .terminal .line-fail  { color: var(--coral); }
  .terminal .line-info  { color: var(--sky); }
  .terminal .line-step  { color: var(--text-mid); }
  .terminal .line-wait  { color: var(--amber); font-style: italic; }
  .terminal .line-retry {
    color: var(--amber);
    font-weight: 600;
    border-top: 1px dashed rgba(245, 179, 66, 0.4);
    border-bottom: 1px dashed rgba(245, 179, 66, 0.4);
    padding: 0.3rem 0;
    margin: 0.35rem 0;
    display: block;
    letter-spacing: 0.05em;
  }

  /* ── Plan card ───────────────────────────────────────────────────────── */
  .plan-card {
    background: var(--bg-panel);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    height: 420px;
    overflow-y: auto;
  }
  .plan-card h4 {
    font-family: 'Inter Tight', sans-serif;
    color: var(--text-hi);
    margin: 0 0 0.2rem 0;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
  }
  .plan-sub { color: var(--text-dim); font-size: 0.78rem; margin-bottom: 1rem; }
  .plan-section {
    font-family: 'Inter Tight', sans-serif;
    color: var(--text-dim);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
    margin: 0.9rem 0 0.4rem 0;
  }
  .plan-list { margin: 0; padding-left: 1.15rem; color: var(--text-mid); font-size: 0.86rem; line-height: 1.75; }
  .plan-list li { margin-bottom: 0.12rem; }
  .plan-list.no-bullets { list-style: none; padding-left: 0; }
  .plan-meta { color: var(--text-dim); font-size: 0.78rem; }

  .plan-method {
    display: inline-block;
    min-width: 3.3rem;
    padding: 0.08rem 0.5rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    text-align: center;
    margin-right: 0.55rem;
  }
  .method-GET    { background: rgba(96, 165, 250, 0.2); color: var(--sky); }
  .method-POST   { background: rgba(74, 222, 128, 0.2); color: var(--emerald); }
  .method-PUT    { background: rgba(245, 179, 66, 0.2); color: var(--amber); }
  .method-DELETE { background: rgba(244, 116, 116, 0.2); color: var(--coral); }

  /* ── Banners ─────────────────────────────────────────────────────────── */
  .banner {
    padding: 0.9rem 1.2rem;
    border-radius: 8px;
    font-size: 0.92rem;
    font-weight: 500;
    margin-bottom: 1rem;
    border: 1px solid;
    font-family: 'Inter', sans-serif;
  }
  .banner-ok   { background: var(--emerald-soft); border-color: rgba(74, 222, 128, 0.35); color: var(--emerald); }
  .banner-fail { background: var(--coral-soft); border-color: rgba(244, 116, 116, 0.4); color: var(--coral); }
  .banner-warn { background: var(--amber-soft); border-color: rgba(245, 179, 66, 0.4); color: var(--amber); }

  /* ── Buttons ─────────────────────────────────────────────────────────── */
  .stButton > button {
    background: linear-gradient(135deg, #f5b342 0%, #e89a2f 100%);
    color: #1a1330;
    border: 0;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0.6rem 1.4rem;
    transition: all 0.18s ease;
    box-shadow: 0 4px 14px rgba(245, 179, 66, 0.25);
  }
  .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(245, 179, 66, 0.35);
    filter: brightness(1.05);
  }
  .stButton > button:focus { box-shadow: 0 0 0 3px rgba(245, 179, 66, 0.3); }

  .stDownloadButton > button {
    background: var(--emerald-soft);
    color: var(--emerald);
    border: 1px solid rgba(74, 222, 128, 0.45);
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    padding: 0.6rem 1.4rem;
    box-shadow: none;
  }
  .stDownloadButton > button:hover {
    background: rgba(74, 222, 128, 0.18);
    transform: translateY(-1px);
  }

  /* ── Inputs ──────────────────────────────────────────────────────────── */
  .stTextArea textarea {
    background: var(--bg-input);
    border: 1px solid var(--border-mid);
    color: var(--text-hi);
    border-radius: 7px;
    font-family: 'Inter', sans-serif;
    font-size: 0.94rem;
    line-height: 1.55;
  }
  .stTextArea textarea:focus {
    border-color: rgba(245, 179, 66, 0.55);
    box-shadow: 0 0 0 3px rgba(245, 179, 66, 0.12);
  }
  .stTextArea textarea::placeholder { color: var(--text-dim); }

  /* ── Tabs ────────────────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0.15rem;
    border-bottom: 1px solid var(--border-soft);
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    padding: 0.6rem 1.1rem;
    color: var(--text-low);
    font-family: 'Inter Tight', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    transition: color 0.15s ease;
  }
  .stTabs [data-baseweb="tab"]:hover { color: var(--text-mid); }
  .stTabs [aria-selected="true"] {
    color: var(--amber);
    border-bottom: 2px solid var(--amber);
  }

  /* ── Expander ────────────────────────────────────────────────────────── */
  .streamlit-expanderHeader, [data-testid="stExpander"] summary {
    font-family: 'Inter Tight', sans-serif;
    font-size: 0.85rem;
    color: var(--text-low);
  }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Small inline SVG logo mark (two stacked offset squares — microservices).
LOGO_SVG = """
<svg viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg" class="ms-mark">
  <defs>
    <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f5b342"/>
      <stop offset="100%" stop-color="#f47474"/>
    </linearGradient>
    <linearGradient id="lg2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#60a5fa"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="18" height="18" rx="3" fill="url(#lg1)" opacity="0.95"/>
  <rect x="14" y="14" width="18" height="18" rx="3" fill="url(#lg2)" opacity="0.95"/>
</svg>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

if "result"           not in st.session_state: st.session_state.result           = None
if "thread_id"        not in st.session_state: st.session_state.thread_id        = None
if "status"           not in st.session_state: st.session_state.status           = None
if "pending_input"    not in st.session_state: st.session_state.pending_input    = None
if "pending_kind"     not in st.session_state: st.session_state.pending_kind     = None
if "attempt_done"     not in st.session_state: st.session_state.attempt_done     = set()
if "last_retries"     not in st.session_state: st.session_state.last_retries     = 0


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(
    f'<div class="ms-header">{LOGO_SVG}<h1 class="ms-title">Microservice Studio</h1></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="ms-subtitle">'
    'Describe the backend you want, and a coordinated team of AI agents will '
    'architect, code, review, test, debug, and package a production-ready '
    'FastAPI microservice in real time — complete with API design, database '
    'models, validation, testing, Dockerization, and deployment-ready infrastructure.'
    '</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants & helpers
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

# Chips that participate in the developer→sec/qa→dockerize retry loop.
RETRY_LOOP_CHIPS = {"developer", "security", "qa", "dockerize"}


def render_timeline(active_set, status, completed):
    chips = []
    terminal = status in ("rejected", "failed")
    for key, label in AGENT_PIPELINE:
        if key in completed:
            chips.append(f'<span class="chip chip-done">✓ {label}</span>')
        elif key in active_set and not terminal:
            chips.append(f'<span class="chip chip-active"><span class="dot"></span>{label}</span>')
        elif status == "failed" and key in active_set:
            chips.append(f'<span class="chip chip-failed">✕ {label}</span>')
        else:
            chips.append(f'<span class="chip chip-pending">○ {label}</span>')
    return f'<div class="agent-row">{"".join(chips)}</div>'


def render_log(logs, waiting_message=None):
    out = []
    for line in logs:
        css_class = "line-step"
        lower = line.lower()
        if line.startswith("--- "):
            out.append(f'<span class="line-retry">{html_lib.escape(line)}</span>')
            continue
        if "approved" in lower or "passed" in lower or "generated." in lower:
            css_class = "line-ok"
        elif "failed" in lower or "rejected" in lower or "error" in lower or "issue(s) found" in lower:
            css_class = "line-fail"
        elif (lower.startswith("[validator]") or lower.startswith("[architect]")
              or lower.startswith("[developer]")):
            css_class = "line-info"
        out.append(f'<span class="{css_class}">{html_lib.escape(line)}</span>')
    if waiting_message:
        out.append(f'<span class="line-wait">… {html_lib.escape(waiting_message)}</span>')
    return '<div class="terminal">' + "\n".join(out) + '</div>'


def render_plan_card(plan_dict):
    if not plan_dict:
        return '<div class="plan-card"><div class="plan-sub">No plan yet.</div></div>'

    models = plan_dict.get("models", []) or []
    endpoints = plan_dict.get("endpoints", []) or []
    notes = plan_dict.get("notes", "") or ""

    parts = ['<div class="plan-card">']
    parts.append('<h4>Architecture plan</h4>')
    parts.append(f'<div class="plan-sub">{len(models)} model · {len(endpoints)} endpoint</div>')

    if models:
        parts.append('<div class="plan-section">Models</div>')
        for m in models:
            name = m.get("name", "?")
            table = m.get("table_name", "?")
            fields = m.get("fields", []) or []
            parts.append(
                f'<div style="margin-bottom:0.45rem;">'
                f'<span style="color:var(--text-hi);font-weight:600;">{html_lib.escape(name)}</span>'
                f' <span class="plan-meta">· table: {html_lib.escape(table)}</span>'
                f'</div>'
            )
            parts.append('<ul class="plan-list">')
            parts.append('<li><span class="plan-meta">id: Integer (auto)</span></li>')
            for f in fields:
                fname = f.get("name", "?")
                ftype = f.get("type", "?")
                nullable = "nullable" if f.get("nullable", True) else "required"
                parts.append(
                    f'<li>{html_lib.escape(fname)}: {html_lib.escape(ftype)} '
                    f'<span class="plan-meta">· {nullable}</span></li>'
                )
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
                f'<code style="color:var(--text-hi);background:transparent;font-family:JetBrains Mono,monospace;">'
                f'{html_lib.escape(path)}</code>'
                f' <span class="plan-meta">— {html_lib.escape(desc)}</span>'
                f'</li>'
            )
        parts.append('</ul>')

    if notes:
        parts.append('<div class="plan-section">Notes</div>')
        parts.append(f'<div style="color:var(--text-mid); font-size:0.86rem;">{html_lib.escape(notes)}</div>')

    parts.append('</div>')
    return "".join(parts)


def show_progressive_section(container, snapshot_state):
    plan       = snapshot_state.get("architecture_plan")
    models_py  = snapshot_state.get("models_py")
    main_py    = snapshot_state.get("main_py")
    test_cases = snapshot_state.get("test_cases")
    dockerfile = snapshot_state.get("dockerfile")
    qa_res     = snapshot_state.get("qa_results")

    with container.container():
        st.markdown('<div class="section-label">Artifacts</div>', unsafe_allow_html=True)

        tab_specs = [("Plan", "plan", plan)]
        if main_py:
            tab_specs.append(("main.py", "python", main_py))
        if models_py:
            tab_specs.append(("models.py", "python", models_py))
        if test_cases and qa_res in ("pass", "fail"):
            tab_specs.append(("tests", "python", test_cases))
        if dockerfile:
            tab_specs.append(("Dockerfile", "dockerfile", dockerfile))

        tabs = st.tabs([spec[0] for spec in tab_specs])
        for tab, (_, lang, content) in zip(tabs, tab_specs):
            with tab:
                if lang == "plan":
                    st.markdown(render_plan_card(content), unsafe_allow_html=True)
                else:
                    st.code(content, language=lang, height=420)


def security_failed(result):
    return result.get("security_approved") is False and bool(result.get("security_feedback"))


def qa_failed(result):
    return result.get("qa_results") == "fail"


def completed_from_state(state, run_status):
    done = set()
    if state.get("architecture_plan"):
        done.add("validator")
        done.add("architect")
    if state.get("models_py") and state.get("main_py"):
        done.add("developer")
    if state.get("security_approved") is True:
        done.add("security")
    if state.get("qa_results") == "pass":
        done.add("qa")
    if state.get("dockerfile"):
        done.add("dockerize")
    if run_status == "success":
        done.update(k for k, _ in AGENT_PIPELINE)
    return done


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
    st.session_state.attempt_done  = set()
    st.session_state.last_retries  = 0
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
    timeline_box  = st.empty()
    artifacts_box = st.empty()
    st.markdown('<div class="section-label">Agent activity</div>', unsafe_allow_html=True)
    log_box = st.empty()

    timeline_box.markdown(
        render_timeline({"validator"}, "running", st.session_state.attempt_done),
        unsafe_allow_html=True,
    )

    logs = []
    accumulated_state = {}
    retry_count_seen = 0

    def predict_active(just_finished_node, completed_so_far):
        nxt = set()
        if just_finished_node == "validator": nxt.add("architect")
        elif just_finished_node == "architect": nxt.add("developer")
        elif just_finished_node == "developer":
            nxt.update({"security", "qa"})
        elif just_finished_node in ("security", "qa"):
            if "security" not in completed_so_far: nxt.add("security")
            if "qa"       not in completed_so_far: nxt.add("qa")
            if {"security", "qa"} <= completed_so_far: nxt.add("dockerize")
        return nxt - completed_so_far

    def waiting_label(active):
        if not active: return None
        labels = {
            "validator": "validator running",
            "architect": "architect designing the API",
            "developer": "developer writing code",
            "security":  "security scanning code",
            "qa":        "QA generating and running tests",
            "dockerize": "dockerize packaging",
        }
        if {"security", "qa"} <= active:
            return "security and QA running in parallel"
        return ", ".join(labels[a] for a in active if a in labels)

    for event in graph.stream(stream_input, config=config, stream_mode="updates"):
        # Detect retry: increment_retry appears as its own event.
        if "increment_retry" in event.keys():
            retry_count_seen += 1
            logs.append(f"--- Retry attempt {retry_count_seen + 1} starting ---")
            # Only reset chips that will actually re-run. Validator+Architect stay green.
            st.session_state.attempt_done -= RETRY_LOOP_CHIPS

        nodes_in_event = [n for n in event.keys()
                          if n not in ("__start__", "verifier_join", "increment_retry")]

        latest_finished = None

        for node in nodes_in_event:
            node_state = event[node]
            if not isinstance(node_state, dict):
                continue

            # Append agent logs without dedup. Retries emit identical starter
            # lines and we want to see them every time.
            for line in node_state.get("agent_logs", []) or []:
                logs.append(line)
            for k, v in node_state.items():
                if k != "agent_logs":
                    accumulated_state[k] = v
            accumulated_state["agent_logs"] = logs

            chip_key = NODE_TO_CHIP.get(node)
            if chip_key:
                st.session_state.attempt_done.add(chip_key)
                latest_finished = chip_key

        finished_now = {NODE_TO_CHIP.get(n) for n in nodes_in_event if NODE_TO_CHIP.get(n)}
        active_set = set()
        if "security" in finished_now or "qa" in finished_now:
            active_set = predict_active("security", st.session_state.attempt_done)
        elif latest_finished:
            active_set = predict_active(latest_finished, st.session_state.attempt_done)

        waiting_msg = waiting_label(active_set)

        timeline_box.markdown(
            render_timeline(active_set, "running", st.session_state.attempt_done),
            unsafe_allow_html=True,
        )
        show_progressive_section(artifacts_box, accumulated_state)
        log_box.markdown(render_log(logs, waiting_message=waiting_msg), unsafe_allow_html=True)

    snapshot = graph.get_state(config)
    final    = snapshot.values
    if snapshot.next:
        new_status = "needs_human"
    else:
        new_status = final.get("status") or "failed"

    timeline_box.markdown(
        render_timeline(set(), new_status, st.session_state.attempt_done),
        unsafe_allow_html=True,
    )

    st.session_state.result       = final
    st.session_state.status       = new_status
    st.session_state.last_retries = final.get("retries", 0)
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

    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    done = completed_from_state(result, status)
    st.markdown(render_timeline(set(), status, done), unsafe_allow_html=True)

    final_container = st.empty()
    show_progressive_section(final_container, result)

    st.markdown('<div class="section-label">Download</div>', unsafe_allow_html=True)
    zip_buf = create_zip(result)
    st.download_button(
        label="Download project zip",
        data=zip_buf,
        file_name="service.zip",
        mime="application/zip",
    )

    with st.expander("Agent activity log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

# ── Rejected at validator ────────────────────────────────────────────────────
elif status == "rejected" and result:
    reasons = result.get("error_messages") or ["Input did not pass validation."]
    st.markdown(
        f'<div class="banner banner-fail">Input rejected: {reasons[-1]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-label">Agent activity</div>', unsafe_allow_html=True)
    st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

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

    # HITL action moved to the top — it's the priority right now.
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

    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    done = completed_from_state(result, status)
    st.markdown(render_timeline(set(), status, done), unsafe_allow_html=True)

    final_container = st.empty()
    show_progressive_section(final_container, result)

    if sec_bad:
        st.markdown('<div class="section-label">Security findings</div>', unsafe_allow_html=True)
        st.code(result.get("security_feedback") or "(no detail)", language="text")
    if qa_bad:
        st.markdown('<div class="section-label">QA output</div>', unsafe_allow_html=True)
        st.code(result.get("qa_output") or "(no detail)", language="text")

    with st.expander("Agent activity log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

    if retry_clicked:
        clarified = new_req.strip() or result.get("user_requirements", "")
        st.session_state.status        = "running"
        st.session_state.pending_input = Command(
            resume={"action": "retry", "clarified_requirements": clarified}
        )
        st.session_state.pending_kind  = "resume"
        st.session_state.attempt_done -= RETRY_LOOP_CHIPS
        st.rerun()

    if accept_clicked:
        st.session_state.status        = "running"
        st.session_state.pending_input = Command(resume={"action": "accept"})
        st.session_state.pending_kind  = "resume"
        st.rerun()

# ── Accepted partial ────────────────────────────────────────────────────────
elif status == "accepted_partial" and result:
    st.markdown(
        '<div class="banner banner-warn">Accepted partial output. The code did not pass all verifiers — review before using.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    done = completed_from_state(result, status)
    st.markdown(render_timeline(set(), status, done), unsafe_allow_html=True)

    final_container = st.empty()
    show_progressive_section(final_container, result)

    if result.get("main_py") and result.get("models_py"):
        if not result.get("dockerfile"):  result["dockerfile"]  = ""
        if not result.get("test_cases"):  result["test_cases"]  = "# tests were not finalized"
        zip_buf = create_zip(result)
        st.markdown('<div class="section-label">Download</div>', unsafe_allow_html=True)
        st.download_button(
            label="Download partial project zip",
            data=zip_buf,
            file_name="service_partial.zip",
            mime="application/zip",
        )

    with st.expander("Agent activity log"):
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)

# ── Failed ──────────────────────────────────────────────────────────────────
elif status == "failed":
    msg = "Generation failed."
    if result and result.get("error_messages"):
        msg = result["error_messages"][-1]
    st.markdown(f'<div class="banner banner-fail">{msg}</div>', unsafe_allow_html=True)
    if result:
        st.markdown('<div class="section-label">Agent activity</div>', unsafe_allow_html=True)
        st.markdown(render_log(result.get("agent_logs", [])), unsafe_allow_html=True)