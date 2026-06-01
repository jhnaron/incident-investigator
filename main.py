import streamlit as st
from dotenv import load_dotenv
import os
import requests

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501")

APP_ICON_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="7" fill="#1a2335"/>
  <rect x="1" y="1" width="30" height="30" rx="6" stroke="#c8a96e" stroke-width="1.2"/>
  <text x="5" y="15" font-family="monospace" font-size="8" fill="#c8a96e" font-weight="bold">&gt;_</text>
  <line x1="5" y1="19" x2="27" y2="19" stroke="#c8a96e" stroke-width="0.8" opacity="0.4"/>
  <line x1="5" y1="22" x2="21" y2="22" stroke="#c8a96e" stroke-width="0.8" opacity="0.4"/>
  <line x1="5" y1="25" x2="24" y2="25" stroke="#c8a96e" stroke-width="0.8" opacity="0.4"/>
</svg>"""

CUSTOM_CSS = """
<style>
[data-testid="stHeader"] {
    background-color: #111827 !important;
    border-bottom: 1px solid #1a2335 !important;
}
[data-testid="stAppViewContainer"] > .main { background-color: #111827; }
[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}
#ii-canvas {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none; z-index: 0;
}
.fork-btn {
    position: fixed; top: 9px; right: 130px; z-index: 9999;
    font-family: monospace; font-size: 11px; color: #c8a96e;
    background: #1a2335; border: 1px solid #c8a96e; border-radius: 5px;
    padding: 4px 10px; text-decoration: none; transition: background 0.2s;
}
.fork-btn:hover { background: #2a3548; color: #e8dcc8; }
.user-tag { font-family: monospace; font-size: 11px; color: #8892a0; }
.user-tag span { color: #c8a96e; }
.logout-btn {
    font-family: monospace; font-size: 11px; color: #8892a0;
    background: transparent; border: 1px solid #2a3548; border-radius: 5px;
    padding: 3px 10px; text-decoration: none; transition: border-color 0.2s, color 0.2s;
}
.logout-btn:hover { border-color: #c8a96e; color: #c8a96e; }
.hero-title { font-family: monospace; font-size: 20px; font-weight: 700; color: #e8dcc8; letter-spacing: 0.03em; line-height: 1.2; }
.hero-sub { font-family: monospace; font-size: 12px; color: #8892a0; margin-top: 3px; }
.section-header {
    font-family: monospace; font-size: 11px; color: #c8a96e;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #2a3548;
}
.btn-loading {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    width: 100%; background: #1a2410; border: 1px solid #3a5020; border-radius: 6px;
    padding: 10px 24px; font-family: monospace; font-size: 13px;
    font-weight: 700; letter-spacing: 0.08em; color: #6a8a50;
    text-transform: uppercase; cursor: not-allowed; box-sizing: border-box;
}
.btn-spinner {
    width: 14px; height: 14px;
    border: 2px solid #3a5020; border-top-color: #c8a96e;
    border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px #27ae60; }
    50% { opacity: 0.4; box-shadow: 0 0 2px #27ae60; }
}
[data-testid="stSpinner"] { display: none !important; }

/* terminal */
.terminal {
    background: #0d1117; border: 1px solid #2a3548; border-radius: 8px;
    overflow: hidden; min-height: 340px; max-height: 520px;
    display: flex; flex-direction: column;
}
.terminal-titlebar {
    background: #161b22; border-bottom: 1px solid #2a3548;
    padding: 7px 12px; display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
.terminal-dot-r { background: #3a2020; border: 1px solid #5a2020; }
.terminal-dot-y { background: #2a2a14; border: 1px solid #4a4014; }
.terminal-dot-g { background: #142a14; border: 1px solid #1a4a1a; }
.terminal-dot-r.active { background: #c0392b; border-color: #e74c3c; }
.terminal-dot-y.active { background: #c8a96e; border-color: #e8c888; }
.terminal-dot-g.active { background: #27ae60; border-color: #2ecc71; }
.terminal-label { font-family: monospace; font-size: 11px; color: #4a5a6e; margin-left: 4px; }
.terminal-body { padding: 1rem 1.25rem; overflow-y: auto; flex: 1; }
.terminal-body::-webkit-scrollbar { width: 4px; }
.terminal-body::-webkit-scrollbar-track { background: #0d1117; }
.terminal-body::-webkit-scrollbar-thumb { background: #2a3548; border-radius: 2px; }
.terminal-prompt { font-family: monospace; font-size: 12px; color: #4a5a6e; margin-bottom: 10px; }
.terminal-prompt span { color: #c8a96e; }

/* tool call line */
.t-line { font-family: monospace; font-size: 12px; line-height: 1.9; display: flex; align-items: baseline; gap: 6px; }
.t-arrow { color: #4a5a6e; }
.t-action { color: #8892a0; }
.t-file { color: #c8a96e; font-weight: 600; }

/* reasoning line — italicised, dimmer, indented */
.t-reasoning {
    font-family: monospace; font-size: 11px; color: #5a6a7a;
    font-style: italic; line-height: 1.7;
    padding-left: 12px;
    border-left: 2px solid #1e2a3a;
    margin: 4px 0 6px 0;
}

.t-idle { color: #2a3548; font-style: italic; font-size: 12px; }
.t-thinking { font-family: monospace; font-size: 11px; color: #c8a96e; margin-top: 8px; opacity: 0.6; }
.t-done { color: #4a7a4a; font-style: italic; font-size: 11px; margin-top: 8px; }

.show-report-bar { margin-top: 1.5rem; display: flex; align-items: center; gap: 12px; }
.show-report-pulse {
    width: 8px; height: 8px; border-radius: 50%;
    background: #27ae60; box-shadow: 0 0 6px #27ae60; flex-shrink: 0;
    animation: pulse 1.5s ease-in-out infinite;
}
.show-report-label { font-family: monospace; font-size: 12px; color: #8892a0; }
.show-report-label span { color: #c8a96e; }

/* inputs */
[data-testid="stSelectbox"] > div > div {
    background: #1a2335 !important; border: 1px solid #2a3548 !important;
    color: #e8dcc8 !important; font-family: monospace !important;
    font-size: 13px !important; border-radius: 6px !important;
}
[data-testid="stTextArea"] textarea {
    background: #1a2335 !important; border: 1px solid #2a3548 !important;
    color: #e8dcc8 !important; font-family: monospace !important;
    font-size: 13px !important; border-radius: 6px !important;
    line-height: 1.6 !important; transition: border-color 0.2s !important;
}
[data-testid="stTextArea"] textarea:not(:placeholder-shown) { border-color: #c8a96e !important; }
[data-testid="stTextArea"] textarea:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 1px rgba(200,169,110,0.15) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #4a5a6e !important; }
[data-testid="stTextArea"] label, [data-testid="stSelectbox"] label {
    font-family: monospace !important; font-size: 11px !important;
    color: #c8a96e !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
[data-testid="stButton"] > button[kind="primary"]:not([disabled]) {
    background: #c8a96e !important; color: #111827 !important;
    border: none !important; font-family: monospace !important;
    font-weight: 700 !important; font-size: 13px !important;
    letter-spacing: 0.08em !important; border-radius: 6px !important;
    padding: 8px 24px !important; text-transform: uppercase !important;
    width: 100% !important; transition: background 0.2s !important;
}
[data-testid="stButton"] > button[kind="primary"]:not([disabled]):hover { background: #e8dcc8 !important; }
[data-testid="stButton"] > button[kind="primary"][disabled] {
    background: #1e2a3a !important; color: #3a4a5a !important; width: 100% !important;
}
[data-testid="stButton"] > button:not([kind="primary"]) { display: none !important; }
[data-testid="stLinkButton"] a {
    font-family: monospace !important; background: #1a2335 !important;
    color: #c8a96e !important; border: 1px solid #c8a96e !important;
    border-radius: 6px !important; font-size: 13px !important;
    padding: 8px 20px !important; text-decoration: none !important;
}
[data-testid="stDownloadButton"] > button {
    font-family: monospace !important; font-size: 12px !important;
    color: #c8a96e !important; background: #1a2335 !important;
    border: 1px solid #2a3548 !important; border-radius: 6px !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #c8a96e !important; background: #2a3548 !important;
}
.report-header {
    font-family: monospace; font-size: 11px; color: #c8a96e;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #2a3548;
}
[data-testid="stMarkdown"] h2 {
    font-family: monospace !important; font-size: 13px !important;
    color: #c8a96e !important; letter-spacing: 0.06em !important;
    text-transform: uppercase !important; font-weight: 600 !important;
    margin-top: 1.2rem !important; border: none !important;
}
[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li {
    font-family: monospace !important; font-size: 13px !important;
    color: #e8dcc8 !important; line-height: 1.8 !important;
}
[data-testid="stMarkdown"] code {
    background: #0d1117 !important; color: #c8a96e !important;
    border-radius: 3px !important; font-size: 12px !important;
}
hr { border-color: #2a3548 !important; opacity: 0.5 !important; }
</style>

<canvas id="ii-canvas"></canvas>
<a class="fork-btn" href="https://github.com/jhnaron/incident-investigator" target="_blank">&#x2442; fork</a>

<script>
(function startCanvas() {
    var canvas = document.getElementById('ii-canvas');
    if (!canvas) { setTimeout(startCanvas, 300); return; }
    var ctx = canvas.getContext('2d');
    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resize();
    window.addEventListener('resize', resize);
    var particles = [];
    for (var i = 0; i < 45; i++) {
        particles.push({
            x: Math.random() * canvas.width, y: Math.random() * canvas.height,
            r: Math.random() * 1.6 + 0.3,
            vx: (Math.random() - 0.5) * 0.25, vy: (Math.random() - 0.5) * 0.25,
            alpha: Math.random() * 0.12 + 0.03
        });
    }
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(function(p) {
            ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(200,169,110,' + p.alpha + ')'; ctx.fill();
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0) p.x = canvas.width; if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height; if (p.y > canvas.height) p.y = 0;
        });
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
"""

LOADING_BTN_HTML = """
<div class="btn-loading">
    <div class="btn-spinner"></div>
    Investigating...
</div>
"""

# steps is a list of dicts: {type: "reasoning"|"tool", content: str|(action,file)}
def terminal_html(steps: list, status: str = "idle") -> str:
    dot_r = "terminal-dot terminal-dot-r" + (" active" if status == "running" else "")
    dot_y = "terminal-dot terminal-dot-y" + (" active" if status == "running" else "")
    dot_g = "terminal-dot terminal-dot-g" + (" active" if status == "done" else "")
    label = {"idle": "waiting...", "running": "investigating...", "done": "done"}.get(status, "")

    if not steps:
        lines_html = '<div class="t-line"><span class="t-idle">// waiting for investigation...</span></div>'
    else:
        lines_html = ""
        for step in steps:
            if step["type"] == "reasoning":
                # Escape any HTML in the reasoning text
                text = step["content"].replace("<", "&lt;").replace(">", "&gt;")
                lines_html += f'<div class="t-reasoning">{text}</div>'
            elif step["type"] == "tool":
                action, file = step["content"]
                lines_html += (
                    f'<div class="t-line">'
                    f'<span class="t-arrow">&gt;</span>'
                    f'<span class="t-action">{action}</span>'
                    f'<span class="t-file">{file}</span>'
                    f'</div>'
                )
        if status == "running":
            lines_html += '<div class="t-thinking">&#9607; thinking...</div>'
        elif status == "done":
            lines_html += '<div class="t-done">// investigation complete</div>'

    repo = st.session_state.get('current_repo', '')
    return f"""
    <div class="terminal">
        <div class="terminal-titlebar">
            <div class="{dot_r}"></div>
            <div class="{dot_y}"></div>
            <div class="{dot_g}"></div>
            <span class="terminal-label">{label}</span>
        </div>
        <div class="terminal-body">
            <div class="terminal-prompt">$ investigate <span>{repo}</span></div>
            {lines_html}
        </div>
    </div>
    """

st.set_page_config(page_title="Incident Investigator", page_icon="🔍", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown('<div id="report-anchor"></div>', unsafe_allow_html=True)

def show_login():
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;padding:3rem 0 1.5rem 0;">
            {APP_ICON_SVG}
            <div style="font-family:monospace;font-size:22px;font-weight:700;color:#e8dcc8;letter-spacing:0.04em;margin-top:12px;">Incident Investigator</div>
            <div style="font-family:monospace;font-size:12px;color:#8892a0;margin-top:6px;">Locates the source of the error in your codebase and generates a report using Claude.</div>
        </div>
        """, unsafe_allow_html=True
    )
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&scope=public_repo&redirect_uri={REDIRECT_URI}"
    )
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.link_button("Login with GitHub", auth_url, use_container_width=True)

def exchange_code_for_token(code: str) -> str | None:
    r = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={"client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET,
              "code": code, "redirect_uri": REDIRECT_URI}
    )
    return r.json().get("access_token")

def get_github_user(token: str) -> dict:
    return requests.get("https://api.github.com/user",
                        headers={"Authorization": f"Bearer {token}"}).json()

def get_user_repos(token: str) -> list[dict]:
    return requests.get("https://api.github.com/user/repos",
                        headers={"Authorization": f"Bearer {token}"},
                        params={"visibility": "public", "sort": "updated", "per_page": 50}).json()

def show_app():
    from app.agent import run_investigation

    username = st.session_state.github_user

    if "logout" in st.query_params:
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

    if "repos" not in st.session_state:
        with st.spinner("loading repositories..."):
            st.session_state.repos = get_user_repos(st.session_state.github_token)
    if "running" not in st.session_state:
        st.session_state.running = False
    if "report" not in st.session_state:
        st.session_state.report = None
    if "show_report" not in st.session_state:
        st.session_state.show_report = False
    if "report_repo" not in st.session_state:
        st.session_state.report_repo = None

    repo_names = [r["full_name"] for r in st.session_state.repos]

    col_hero, col_repo, col_user = st.columns([3, 3, 2])

    with col_hero:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:14px;padding:0 0 0.3rem 0;">'
            f'{APP_ICON_SVG}'
            f'<div>'
            f'<div class="hero-title">Incident Investigator</div>'
            f'<div class="hero-sub">Locates the source of the error in your codebase and generates a report using Claude.</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    with col_repo:
        selected_repo = st.selectbox("Repository", repo_names, label_visibility="visible")
        st.session_state.current_repo = selected_repo

    with col_user:
        st.markdown(
            f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;padding-top:4px;">'
            f'<div class="user-tag">logged in as <span>{username}</span></div>'
            f'<a class="logout-btn" href="?logout=1">logout</a>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-header">Stack Trace / Error</div>', unsafe_allow_html=True)
        stack_trace = st.text_area(
            "stack_trace_input",
            height=320,
            placeholder="Traceback (most recent call last):\n  File \"app/main.py\", line 42, in handler\n    result = process(data)\nAttributeError: 'NoneType' object has no attribute 'encode'",
            disabled=st.session_state.running,
            label_visibility="collapsed"
        )
        st.write("")

        btn_slot = st.empty()
        if st.session_state.running:
            btn_slot.markdown(LOADING_BTN_HTML, unsafe_allow_html=True)
            investigate = False
        else:
            investigate = btn_slot.button(
                "Investigate",
                type="primary",
                disabled=not stack_trace,
                use_container_width=True
            )

    with col_right:
        st.markdown('<div class="section-header">&gt; Reasoning Trace</div>', unsafe_allow_html=True)
        console = st.empty()

        if st.session_state.report and not st.session_state.running:
            console.markdown(
                terminal_html(st.session_state.get("last_steps", []), status="done"),
                unsafe_allow_html=True
            )
        else:
            console.markdown(terminal_html([], status="idle"), unsafe_allow_html=True)

        if st.session_state.report and not st.session_state.show_report:
            st.markdown(
                '<div class="show-report-bar">'
                '<div class="show-report-pulse"></div>'
                '<div class="show-report-label">Report ready — <span>click below to expand</span></div>'
                '</div>',
                unsafe_allow_html=True
            )
            if st.button("Show Report ↓", type="primary"):
                st.session_state.show_report = True
                st.rerun()

    if investigate and stack_trace and selected_repo:
        st.session_state.running = True
        st.session_state.report = None
        st.session_state.show_report = False
        btn_slot.markdown(LOADING_BTN_HTML, unsafe_allow_html=True)
        steps = []

        def on_tool_call(event_type: str, content):
            if event_type == "reasoning":
                steps.append({"type": "reasoning", "content": content})
            elif event_type == "tool":
                tool_name, label = content
                action = "reading " if tool_name == "fetch_file" else "listing "
                file = label if tool_name == "fetch_file" else "repository tree"
                steps.append({"type": "tool", "content": (action, file)})
            console.markdown(terminal_html(steps, status="running"), unsafe_allow_html=True)

        report = run_investigation(
            repo_full_name=selected_repo,
            stack_trace=stack_trace,
            token=st.session_state.github_token,
            on_tool_call=on_tool_call
        )

        st.session_state.running = False
        st.session_state.report = report
        st.session_state.report_repo = selected_repo
        st.session_state.last_steps = steps
        st.rerun()

    if st.session_state.report and st.session_state.show_report:
        st.divider()
        st.markdown('<div id="report-section"></div>', unsafe_allow_html=True)
        st.markdown(
            '<script>document.getElementById("report-section").scrollIntoView({behavior:"smooth"});</script>',
            unsafe_allow_html=True
        )
        col_rh, col_dl = st.columns([5, 1])
        with col_rh:
            st.markdown('<div class="report-header">&gt; Investigation Report</div>', unsafe_allow_html=True)
        with col_dl:
            st.download_button(
                label="⬇ download .md",
                data=st.session_state.report,
                file_name=f"incident-report-{st.session_state.report_repo.replace('/', '-')}.md",
                mime="text/markdown"
            )
        st.markdown(st.session_state.report)

params = st.query_params

if "github_token" not in st.session_state:
    if "code" in params:
        with st.spinner("authenticating with github..."):
            token = exchange_code_for_token(params["code"])
            if token:
                user = get_github_user(token)
                st.session_state.github_token = token
                st.session_state.github_user = user.get("login")
                st.query_params.clear()
                st.rerun()
            else:
                st.error("GitHub authentication failed. Please try again.")
                show_login()
    else:
        show_login()
else:
    show_app()
