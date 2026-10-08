"""
FastAPI Backend — REST API for the AI Agent.

Provides endpoints for chat, session management, tool listing,
and health checks. The agent runs locally via Ollama + LangGraph.

Usage:
    uvicorn backend.api:app --reload --port 8000
"""

import sys
import os
import re
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is on path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

DEFAULT_MODEL = GROQ_MODEL if LLM_PROVIDER == "groq" else OLLAMA_MODEL

# ── In-memory session store ──────────────────────────────────
sessions: dict[str, list[dict]] = {}


# ── Pydantic Models ──────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    session_id: str | None = Field(None, description="Session ID for conversation continuity")
    model: str = Field(default=DEFAULT_MODEL, description="Model name (e.g. llama-3.3-70b-versatile or phi3)")
    provider: str | None = Field(default=None, description="LLM provider: 'groq' or 'ollama'")
    temperature: float = Field(default=TEMPERATURE, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    turn: int
    tools_used: list[str]
    processing_time_ms: int


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    created_at: str


class ToolInfo(BaseModel):
    name: str
    description: str
    status: str = "active"


class HealthResponse(BaseModel):
    status: str
    provider: str
    model: str
    ollama_url: str = ""
    timestamp: str


# ── Agent Factory ────────────────────────────────────────────
def create_agent(model_name: str, temperature: float, provider: str | None = None):
    """Create a fresh ReAct agent with the given model config (Groq or Ollama)."""
    # Auto-detect provider if not explicitly given
    if not provider:
        if any(prefix in model_name.lower() for prefix in ["llama", "mixtral", "gemma"]) and "ollama" not in model_name.lower() and LLM_PROVIDER == "groq":
            provider = "groq"
        elif model_name in ["phi3", "mistral"] and not os.getenv("GROQ_API_KEY"):
            provider = "ollama"

    llm = get_llm(
        provider=provider,
        model=model_name,
        temperature=temperature,
    )

    tools = [calculator, knowledge_lookup, get_current_datetime]

    system_message = (
        "You are a friendly, helpful assistant. "
        "Answer the user's questions naturally in plain language. "
        "You can do math, look up tech topics, and check the date. "
        "NEVER show JSON, code blocks, function names, or tool schemas in your answers. "
        "Always remember the user's name and what they told you before."
    )

    return create_react_agent(llm, tools, prompt=system_message)


def build_message_history(session_messages: list) -> list:
    """Convert session messages to LangChain message objects."""
    lc_messages = []
    for msg in session_messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    return lc_messages


def extract_tools_used(result: dict) -> list[str]:
    """Extract names of tools called during agent execution."""
    tools_used = []
    for msg in result.get("messages", []):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc.get("name", "unknown"))
    return tools_used


# Map of tool names to their actual functions
TOOL_MAP = {
    "calculator": calculator,
    "knowledge_lookup": knowledge_lookup,
    "get_current_datetime": get_current_datetime,
}


def fix_raw_tool_call(response_text: str) -> tuple[str, list[str]]:
    """Detect and execute raw tool calls that the model outputted as text.

    Small models like llama3.2 sometimes output tool calls as plain text
    like '{"name": "knowledge_lookup", "parameters": {"topic": "langraph"}}'
    instead of making a proper structured tool call. This function catches
    those, executes the tool, and returns a clean result.

    Returns:
        (cleaned_response, tools_used_list)
    """
    # Pattern: JSON-like string with "name" and "parameters" keys
    pattern = r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"parameters"\s*:\s*(\{[^}]+\})\s*\}'
    match = re.search(pattern, response_text)

    if not match:
        return response_text, []

    tool_name = match.group(1)
    try:
        params = json.loads(match.group(2))
    except json.JSONDecodeError:
        return response_text, []

    if tool_name not in TOOL_MAP:
        return response_text, []

    # Execute the tool
    try:
        tool_fn = TOOL_MAP[tool_name]
        # Call the tool's invoke method with the params
        tool_result = tool_fn.invoke(params)

        # Remove the raw JSON from the response and replace with the result
        cleaned = re.sub(pattern, '', response_text).strip()
        if cleaned:
            return f"{cleaned}\n\n{tool_result}", [tool_name]
        else:
            return str(tool_result), [tool_name]
    except Exception:
        return response_text, []


# ── App Lifecycle ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    active_model = GROQ_MODEL if LLM_PROVIDER == "groq" else OLLAMA_MODEL
    print(f"  Agent API starting | Provider: {LLM_PROVIDER} | Model: {active_model}")
    yield
    print("  Agent API shutting down")


# ── FastAPI App ──────────────────────────────────────────────
app = FastAPI(
    title="AI Agent API",
    description="REST API for an AI agent powered by Groq / Ollama + LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all local frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import HTMLResponse, FileResponse

# ── Endpoints ────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the minimal Agent dashboard."""
    html_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Agent UI (minimal).html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return HTMLResponse("<h1>Agent Backend Running</h1>")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API and LLM provider connection are configured."""
    active_model = GROQ_MODEL if LLM_PROVIDER == "groq" else OLLAMA_MODEL
    return HealthResponse(
        status="ok",
        provider=LLM_PROVIDER,
        model=active_model,
        ollama_url=OLLAMA_BASE_URL if LLM_PROVIDER == "ollama" else "N/A (Groq Cloud)",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/tools", response_model=list[ToolInfo])
async def list_tools():
    """List all available agent tools."""
    return [
        ToolInfo(
            name="Calculator",
            description="Evaluates mathematical expressions (e.g., sqrt(144), 2**10, sin(pi/2))",
        ),
        ToolInfo(
            name="Knowledge Base",
            description="Looks up tech/programming topics (e.g., python, langchain, react)",
        ),
        ToolInfo(
            name="DateTime",
            description="Returns the current date, time, or day of the week",
        ),
    ]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a response.

    If no session_id is provided, a new session is created.
    The agent sees the full conversation history for context.
    """
    start = datetime.now()

    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = []

    # Add user message to session
    sessions[session_id].append({"role": "user", "content": request.message})

    try:
        # Create agent with requested config
        agent = create_agent(request.model, request.temperature, request.provider)

        # Build full history and invoke
        full_history = build_message_history(sessions[session_id])
        result = agent.invoke({"messages": full_history})

        # Extract response
        response_text = result["messages"][-1].content
        tools_used = extract_tools_used(result)

        # Post-process: catch raw JSON tool calls from small models
        response_text, extra_tools = fix_raw_tool_call(response_text)
        tools_used.extend(extra_tools)

        # Save assistant response to session
        sessions[session_id].append({"role": "assistant", "content": response_text})

        elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            turn=len(sessions[session_id]) // 2,
            tools_used=tools_used,
            processing_time_ms=elapsed_ms,
        )

    except Exception as e:
        # Remove the failed user message from history
        sessions[session_id].pop()
        error_msg = str(e)
        if "GROQ_API_KEY" in error_msg or "api_key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail=f"Groq API key error: {error_msg}. Please check GROQ_API_KEY in your .env file.",
            )
        if "Connection refused" in error_msg or "connection" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Connection error: LLM service is unreachable. (If using Ollama, run: ollama serve)",
            )
        raise HTTPException(status_code=500, detail=f"Agent error: {error_msg}")


@app.get("/sessions", response_model=list[SessionInfo])
async def list_sessions():
    """List all active conversation sessions."""
    return [
        SessionInfo(
            session_id=sid,
            message_count=len(msgs),
            created_at=datetime.now().isoformat(),
        )
        for sid, msgs in sessions.items()
    ]


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get the full message history for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": sessions[session_id]}


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session (clear memory)."""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "deleted", "session_id": session_id}
