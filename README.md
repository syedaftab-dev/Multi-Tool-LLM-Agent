# Multi-Tool AI Agent (Groq & Ollama)

A high-performance AI agent project powered by **Groq API** (ultra-fast cloud inference) and **Ollama** (optional local fallback), built with **LangChain** and **LangGraph**. The agent can use tools, remembers conversation context, and includes CLI, Streamlit, and FastAPI + React interfaces.

## Features

- **Groq API support** for ultra-fast LPU inference (e.g., `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`)
- **Ollama support** for 100% offline local models (e.g., `phi3`, `llama3.2`)
- **ReAct-style agent workflow** using LangChain and LangGraph
- **Calculator tool** for math expressions
- **Knowledge base tool** for technical topics
- **Date and time tool**
- **Conversation memory support**
- **Streamlit chat UI** with provider & model switcher
- **FastAPI backend** for API-based chat
- **React + Vite frontend**
- **Unit tests for tools**

## Project Structure

```text
Basic_Agent/
+-- agent.py                  # Basic agent CLI
+-- agent_with_memory.py      # Agent with conversation memory
+-- agent_langgraph.py        # LangGraph-based agent
+-- app.py                    # Streamlit web app
+-- config.py                 # Environment-based configuration
+-- setup.py                  # Environment setup checker
+-- requirements.txt          # Python dependencies
+-- backend/
|   +-- api.py                # FastAPI backend
+-- frontend/
|   +-- package.json          # React frontend dependencies
|   +-- src/                  # Frontend source files
+-- tools/
|   +-- calculator.py
|   +-- datetime_tool.py
|   +-- knowledge_base.py
+-- tests/
    +-- test_tools.py
```

## Requirements

- Python 3.9 or newer
- **Groq API Key** (Free from https://console.groq.com/keys) OR Ollama installed locally
- Node.js and npm (optional, for React frontend)

## Quickstart

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Create your `.env` file (or copy `.env.example`):

```bash
cp .env.example .env
```

3. Add your Groq API key in `.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

*(Optional) If using Ollama locally instead, set `LLM_PROVIDER=ollama` and ensure `ollama serve` is running.*

4. Verify setup:

```bash
python setup.py
```

The `.env` file is ignored by Git, so your local settings stay private.

## Run The Agent

Run the basic agent:

```bash
python agent.py
```

Run the memory-enabled agent:

```bash
python agent_with_memory.py
```

Run the LangGraph agent:

```bash
python agent_langgraph.py
```

Run the Streamlit web UI:

```bash
streamlit run app.py
```

## Run The FastAPI Backend

If needed, install API dependencies:

```bash
pip install fastapi uvicorn pydantic
```

Start the API server:

```bash
uvicorn backend.api:app --reload --port 8000
```

Useful API endpoints:

```text
GET  /health
GET  /tools
POST /chat
GET  /sessions
GET  /sessions/{session_id}
DELETE /sessions/{session_id}
```

## Run The React Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend usually runs at:

```text
http://localhost:5173
```

Make sure the FastAPI backend is running on port `8000` before using the frontend chat.

## Tools

| Tool | Purpose | Example |
| --- | --- | --- |
| Calculator | Evaluates math expressions | `sqrt(144)`, `2**10` |
| Knowledge Base | Looks up technical topics | `python`, `langchain`, `ollama` |
| DateTime | Returns current date and time | `date`, `time`, `full` |

## Run Tests

```bash
python -m pytest tests -v
```

## GitHub Push Commands

If this is a new repository:

```bash
git init
git branch -M main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/Basic_Agent.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Notes

- Do not commit `.env`, `venv/`, `__pycache__/`, `frontend/node_modules/`, or build output.
- Keep Ollama running before starting the agent.
- Use a model that works well with tool calling for best results.
