"""
Streamlit Web UI — Interactive chat interface for the AI Agent.

Provides a beautiful chat UI with model selection, tool status,
and conversation history, powered by the same LangGraph agent.

Usage:
    streamlit run app.py
"""

import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from config import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE
from tools import calculator, knowledge_lookup, get_current_datetime


# ── Page Configuration ───────────────────────────────────────
st.set_page_config(
    page_title="🤖 Local AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for Premium Look ──────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        color: #888;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .tool-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .status-active {
        background: #1a3a1a;
        color: #4ade80;
        border: 1px solid #4ade80;
    }

    .stChatMessage {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    model_name = st.text_input(
        "Ollama Model",
        value=OLLAMA_MODEL,
        help="Model name as pulled in Ollama (e.g., phi3, llama3.2, mistral)",
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=TEMPERATURE,
        step=0.05,
        help="Lower = more focused, Higher = more creative",
    )

    st.markdown("---")

    st.markdown("### 🛠️ Available Tools")

    tools_info = {
        "🧮 Calculator": "Evaluates math expressions",
        "📖 Knowledge Base": "Looks up tech/programming topics",
        "📅 DateTime": "Returns current date and time",
    }

    for tool_name, tool_desc in tools_info.items():
        st.markdown(f"""
        <div class="tool-card">
            <strong>{tool_name}</strong><br>
            <span style="color: #aaa; font-size: 0.85rem;">{tool_desc}</span>
            <span class="status-badge status-active" style="float: right;">Active</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = None
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#666; font-size:0.8rem;'>"
        "Built with Ollama + LangGraph<br>"
        "Runs 100% locally 🔒"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Agent Initialization ────────────────────────────────────
@st.cache_resource
def create_agent(_model_name: str, _temperature: float):
    """Create the LangGraph agent (cached by model config).

    Memory is managed explicitly via session state rather than
    LangGraph's MemorySaver, which is more reliable with Streamlit's
    rerun lifecycle and small language models.
    """
    llm = ChatOllama(
        model=_model_name,
        base_url=OLLAMA_BASE_URL,
        temperature=_temperature,
    )

    tools = [calculator, knowledge_lookup, get_current_datetime]

    system_message = (
        "You are a friendly, helpful assistant. "
        "Answer the user's questions naturally in plain language. "
        "You can do math, look up tech topics, and check the date. "
        "NEVER show JSON, code blocks, function names, or tool schemas in your answers. "
        "Always remember the user's name and what they told you before."
    )

    agent = create_react_agent(
        llm,
        tools,
        prompt=system_message,
    )

    return agent


def build_message_history(session_messages: list) -> list:
    """Convert session state messages to LangChain message objects.

    This ensures the agent always sees the FULL conversation history,
    so it can remember names, context, and prior answers reliably.
    """
    lc_messages = []
    for msg in session_messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    return lc_messages


# ── Main Chat UI ─────────────────────────────────────────────
st.markdown('<h1 class="main-header">Local AI Agent</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Powered by Ollama + LangGraph — runs entirely on your machine</p>',
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything... (try math, tech topics, or current time)"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                agent = create_agent(model_name, temperature)

                # Build FULL conversation history so the agent
                # remembers everything from this session
                full_history = build_message_history(st.session_state.messages)

                result = agent.invoke(
                    {"messages": full_history},
                )

                response = result["messages"][-1].content
                st.markdown(response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            except Exception as e:
                error_msg = f"**Error:** {str(e)}"
                if "Connection refused" in str(e) or "connection" in str(e).lower():
                    error_msg += (
                        "\n\n**Tip:** Make sure Ollama is running! "
                        "Open a terminal and run: `ollama serve`"
                    )
                st.error(error_msg)
