# Basic AI Agent

A local AI agent project powered by Ollama, LangChain, and LangGraph. The agent runs on your machine, can use tools, remembers conversation context, and includes both command-line and web interfaces.

## Features

- Local LLM support through Ollama
- ReAct-style agent workflow using LangChain and LangGraph
- Calculator tool for math expressions
- Knowledge base tool for technical topics
- Date and time tool
- Conversation memory support
- Streamlit chat UI
- FastAPI backend for API-based chat
- React + Vite frontend
- Unit tests for tools

## Project Structure

```text
Basic_Agent/
+-- agent.py                  # Basic agent example
+-- agent_with_memory.py      # Agent with conversation memory
+-- agent_langgraph.py        # LangGraph-based agent
+-- app.py                    # Streamlit web app
+-- config.py                 # Environment-based configuration
+-- setup.py                  # Local setup checker
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
- Node.js and npm, for the React frontend
- Ollama installed locally
- An Ollama model such as `phi3`, `llama3.2`, or `mistral`

## Setup

Clone the project and enter the folder:

```bash
git clone https://github.com/YOUR_USERNAME/Basic_Agent.git
cd Basic_Agent
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Ollama from:

```text
https://ollama.com/download
```

Pull a local model:

```bash
ollama pull phi3
```

Start Ollama:

```bash
ollama serve
```

## Configuration

Create a `.env` file in the project root:

```env
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434
TEMPERATURE=0.1
MAX_TOKENS=1024
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
