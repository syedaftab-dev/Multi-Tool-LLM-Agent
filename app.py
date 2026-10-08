"""
Multi-Tool AI Agent — Minimal Editorial UI Dashboard
Faithfully matching the design, typography, and layout of Agent UI (minimal).html.
"""

import os
import uuid
import datetime
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from config import (
    get_llm,
    LLM_PROVIDER,
    GROQ_MODEL,
    GROQ_API_KEY,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    TEMPERATURE,
)
from tools import calculator, knowledge_lookup, get_current_datetime


# ── Page Configuration ───────────────────────────────────────
st.set_page_config(
    page_title="Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Minimal Theme Matching Agent UI (minimal).html ────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Permanent Dark Theme Variables (Agent Minimal UI) */
:root,
html,
body,
.stApp,
[data-theme] {
  --bg: #141413 !important;
  --panel: #1B1B19 !important;
  --ink: #ECEAE3 !important;
  --mute: #8F8C82 !important;
  --line: #2C2C29 !important;
  --accent: #6FC3A5 !important;
  --accent-ink: #0F1A15 !important;
  --chip: #242421 !important;
}

/* Streamlit Base Containers */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background-color: var(--bg) !important;
  color: var(--ink) !important;
  font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
  background-color: var(--bg) !important;
  border-right: 1px solid var(--line) !important;
  width: 275px !important;
  min-width: 275px !important;
}

section[data-testid="stSidebar"] .block-container {
  padding: 20px 12px !important;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px 18px;
  font-weight: 600;
  font-size: 16px;
  color: var(--ink);
}
.mark {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: var(--accent);
  color: var(--accent-ink);
  display: grid;
  place-items: center;
}
.mark svg {
  width: 15px;
  height: 15px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Sidebar Labels */
.sidebar-label {
  font-size: 12px;
  color: var(--mute);
  padding: 14px 6px 4px;
  letter-spacing: .04em;
  text-transform: uppercase;
  font-weight: 500;
}

/* Tool Items */
.tool-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  color: var(--mute);
  font-size: 14px;
  user-select: none;
}
.tool-item svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  fill: none;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex: none;
}
.dot {
  margin-left: auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
}

/* Top Pill Header */
.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0 20px 0;
  color: var(--mute);
  font-size: 13px;
  max-width: 720px;
  margin: 0 auto;
}
.model-pill {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 5px 12px;
  color: var(--ink);
  font-size: 13px;
  background: var(--panel);
}
.status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.status-pill i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  display: inline-block;
}

/* Main Container */
.main .block-container {
  max-width: 760px;
  padding-top: 1.5rem;
  padding-bottom: 6rem;
}

/* Hero Section */
.hero-box {
  padding: 8vh 0 28px;
  text-align: left;
}
.hero-title {
  font-size: clamp(28px, 4.4vw, 40px);
  font-weight: 600;
  letter-spacing: -.02em;
  line-height: 1.15;
  color: var(--ink);
  margin-bottom: 10px;
}
.hero-sub {
  color: var(--mute);
  font-size: 15px;
  line-height: 1.5;
  margin-bottom: 28px;
}

/* Suggestion Cards */
.card-btn {
  text-align: left;
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color .15s;
  cursor: pointer;
  height: 100%;
}
.card-btn:hover {
  border-color: var(--accent);
}
.card-btn b {
  font-weight: 600;
  color: var(--ink);
  font-size: 14px;
}
.card-btn small {
  color: var(--mute);
  font-size: 13px;
  line-height: 1.4;
}
.card-btn code {
  font: 12px ui-monospace, Menlo, monospace;
  background: var(--chip);
  padding: 2px 6px;
  border-radius: 5px;
  width: fit-content;
  color: var(--ink);
  margin-top: 4px;
}

/* Custom Message Bubbles */
.msg-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px 0;
}
.m-user-row {
  display: flex;
  justify-content: flex-end;
}
.m-user {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--accent) !important;
  color: var(--accent-ink) !important;
  font-size: 15px;
  line-height: 1.5;
  font-weight: 500;
  word-wrap: break-word;
}
.m-assistant-row {
  display: flex;
  justify-content: flex-start;
}
.m-assistant {
  max-width: 88%;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
}
.msg-tag {
  display: block;
  font-size: 11px;
  color: var(--mute);
  letter-spacing: .04em;
  text-transform: uppercase;
  margin-bottom: 4px;
  font-weight: 600;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
  border-color: var(--line) !important;
  background-color: var(--panel) !important;
  border-radius: 12px !important;
}
div[data-testid="stChatInput"]:focus-within {
  border-color: var(--accent) !important;
}
div[data-testid="stChatInput"] textarea {
  color: var(--ink) !important;
  font-family: inherit !important;
}
div[data-testid="stChatInput"] button {
  color: var(--accent) !important;
}

.composer-hint {
  text-align: center;
  font-size: 12px;
  color: var(--mute);
  margin-top: 6px;
}

/* Buttons in sidebar */
div[data-testid="stSidebar"] button {
  border-radius: 8px !important;
  border-color: var(--line) !important;
}
div[data-testid="stSidebar"] button:hover {
  border-color: var(--accent) !important;
}

/* Recent chat rows and delete button fix */
section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
  gap: 6px !important;
  align-items: center !important;
  margin-bottom: 3px !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
  flex: 1 1 auto !important;
  min-width: 0 !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
  flex: 0 0 44px !important;
  width: 44px !important;
  min-width: 44px !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child button {
  width: 42px !important;
  min-width: 42px !important;
  max-width: 42px !important;
  height: 38px !important;
  padding: 0 !important;
  margin: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  border-radius: 8px !important;
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  overflow: visible !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child button:hover {
  border-color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.15) !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child button p {
  font-size: 16px !important;
  line-height: 1 !important;
  margin: 0 !important;
  padding: 0 !important;
  display: inline-block !important;
  overflow: visible !important;
}

/* Primary buttons */
button[kind="primary"] {
  background-color: var(--accent) !important;
  color: var(--accent-ink) !important;
  border: none !important;
  font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Conversation Session Store ───────────────────────────────
if "chats" not in st.session_state:
    init_id = str(uuid.uuid4())
    st.session_state.chats = {
        init_id: {
            "id": init_id,
            "title": "New chat",
            "created_at": datetime.datetime.now(),
            "messages": [],
        }
    }
    st.session_state.current_chat_id = init_id

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.chats:
    if st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
    else:
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {
            "id": new_id,
            "title": "New chat",
            "created_at": datetime.datetime.now(),
            "messages": [],
        }
        st.session_state.current_chat_id = new_id

current_chat = st.session_state.chats[st.session_state.current_chat_id]


# ── Left Sidebar (Matching Agent UI) ─────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="brand">
        <div class="mark">
            <svg viewBox="0 0 24 24"><path d="M12 4v16M4.5 8l15 8M19.5 8l-15 8"/></svg>
        </div>
        Agent
    </div>
    """, unsafe_allow_html=True)

    # New Chat Button
    if st.button("➕  New chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {
            "id": new_id,
            "title": "New chat",
            "created_at": datetime.datetime.now(),
            "messages": [],
        }
        st.session_state.current_chat_id = new_id
        st.rerun()

    # Recent Section
    st.markdown('<div class="sidebar-label">Recent</div>', unsafe_allow_html=True)

    for chat_id, chat_data in list(st.session_state.chats.items()):
        is_active = (chat_id == st.session_state.current_chat_id)
        col_title, col_del = st.columns([0.76, 0.24], gap="small")

        label = chat_data["title"]
        if len(label) > 17:
            label = label[:16] + "…"

        if col_title.button(
            label,
            key=f"item_{chat_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()

        if col_del.button("🗑️", key=f"del_{chat_id}", help="Delete chat"):
            del st.session_state.chats[chat_id]
            if not st.session_state.chats:
                nid = str(uuid.uuid4())
                st.session_state.chats[nid] = {
                    "id": nid,
                    "title": "New chat",
                    "created_at": datetime.datetime.now(),
                    "messages": [],
                }
                st.session_state.current_chat_id = nid
            elif st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
            st.rerun()

    # Tools Section (Exact replica from Agent UI)
    st.markdown('<div class="sidebar-label">Tools</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tool-item">
        <svg viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/></svg>
        <span>Calculator</span>
        <i class="dot"></i>
    </div>
    <div class="tool-item">
        <svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/></svg>
        <span>Tech lookup</span>
        <i class="dot"></i>
    </div>
    <div class="tool-item">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
        <span>Date and time</span>
        <i class="dot"></i>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    # Clear History Button
    if st.button("Clear history", use_container_width=True):
        fresh_id = str(uuid.uuid4())
        st.session_state.chats = {
            fresh_id: {
                "id": fresh_id,
                "title": "New chat",
                "created_at": datetime.datetime.now(),
                "messages": [],
            }
        }
        st.session_state.current_chat_id = fresh_id
        st.rerun()


# ── Agent Setup ──────────────────────────────────────────────
@st.cache_resource
def get_or_create_agent(_provider_name: str, _model_name: str, _temperature: float):
    llm = get_llm(
        provider=_provider_name.lower(),
        model=_model_name,
        temperature=_temperature,
    )
    tools = [calculator, knowledge_lookup, get_current_datetime]
    system_message = (
        "You are a helpful, accurate AI agent. "
        "You have tools for calculations, tech lookup, and current date/time. "
        "Use your tools when appropriate to give precise answers. "
        "Keep answers clean, concise, and formatted in Markdown."
    )
    return create_react_agent(llm, tools, prompt=system_message)


def build_message_history(session_messages: list) -> list:
    lc_messages = []
    for msg in session_messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    return lc_messages


def detect_tag(prompt_or_response: str) -> str:
    low = prompt_or_response.lower()
    if any(k in low for k in ["calculate", "sqrt", "math", "+", "*", "power", "/"]):
        return "Calculator"
    if any(k in low for k in ["langgraph", "langchain", "react", "python", "docker", "api"]):
        return "Tech lookup"
    if any(k in low for k in ["date", "time", "day", "today", "now"]):
        return "Date and time"
    return "Agent"


# ── Main Content Area ────────────────────────────────────────
active_provider = LLM_PROVIDER
active_model = GROQ_MODEL
active_temp = TEMPERATURE


# Hero Section & Suggestion Cards (Shown only when chat is empty)
if len(current_chat["messages"]) == 0:
    st.markdown("""
    <div class="hero-box">
        <h1 class="hero-title">What can I work out for you?</h1>
        <p class="hero-sub">Solve math, look up tech docs, or check the time. I remember everything we've said in this chat.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧮 Math\n\nSolve expressions and equations\n\n`sqrt(144) + 25*3`", use_container_width=True):
            st.session_state["pending_prompt"] = "sqrt(144) + 25*3"
            st.rerun()
    with col2:
        if st.button("📖 Tech lookup\n\nFind docs and explain concepts\n\n`What is LangGraph?`", use_container_width=True):
            st.session_state["pending_prompt"] = "What is LangGraph?"
            st.rerun()
    with col3:
        if st.button("🕒 Date and time\n\nCheck the current moment\n\n`Today's date`", use_container_width=True):
            st.session_state["pending_prompt"] = "Today's date"
            st.rerun()


# Message Stream
if current_chat["messages"]:
    st.markdown('<div class="msg-wrap">', unsafe_allow_html=True)
    for msg in current_chat["messages"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="m-user-row">
                <div class="m-user">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            tag = msg.get("tag", "Agent")
            st.markdown(f"""
            <div class="m-assistant-row">
                <div class="m-assistant">
                    <span class="msg-tag">{tag}</span>
                    <div>{msg["content"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Composer & Input Handling
user_input = st.chat_input("Ask about math, tech docs, or the time")
prompt_to_run = None

if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
    prompt_to_run = st.session_state.pop("pending_prompt")
elif user_input:
    prompt_to_run = user_input

if prompt_to_run:
    # Auto-title chat if still default
    if current_chat["title"] == "New chat":
        clean = prompt_to_run.strip()
        current_chat["title"] = clean[:22] + ("…" if len(clean) > 22 else "")

    # Add user message
    current_chat["messages"].append({"role": "user", "content": prompt_to_run})

    with st.spinner("Working..."):
        try:
            agent = get_or_create_agent(active_provider, active_model, active_temp)
            history = build_message_history(current_chat["messages"])
            result = agent.invoke({"messages": history})

            response_content = result["messages"][-1].content
            tag = detect_tag(prompt_to_run + " " + response_content)

            current_chat["messages"].append({
                "role": "assistant",
                "content": response_content,
                "tag": tag,
            })

            st.rerun()

        except Exception as e:
            err = str(e)
            if "GROQ_API_KEY" in err or "api_key" in err.lower():
                st.error("⚠️ Groq API Key error. Please verify GROQ_API_KEY in your .env file.")
            elif "Connection refused" in err:
                st.error("⚠️ Could not connect to LLM server. (If using Ollama, ensure 'ollama serve' is running)")
            else:
                st.error(f"⚠️ Error: {err}")

st.markdown('<div class="composer-hint">Press Enter to send</div>', unsafe_allow_html=True)
