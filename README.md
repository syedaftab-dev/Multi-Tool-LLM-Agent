<div align="center">

# ⚡ Multi-Tool AI Agent

**Autonomous ReAct Agent powered by Groq LPU Inference, LangChain & LangGraph**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.3+-green.svg)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-v0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Groq LPU](https://img.shields.io/badge/Groq-Ultra--Fast_Inference-red.svg)](https://groq.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<br/>

<!-- Dashboard Screenshot -->
<p align="center">
  <img src="assets/dashboard.png" alt="Multi-Tool AI Agent Dashboard" width="900" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);" />
</p>

*Modern ChatGPT-style dark editorial dashboard with sidebar session management, real-time tool calling, and sub-second Groq responses.*

</div>

---

## 📌 Overview

**Multi-Tool AI Agent** is an end-to-end intelligent assistant built with **LangChain**, **LangGraph**, and **Groq Cloud API** (with offline **Ollama** fallback). The system implements an autonomous **ReAct (Reasoning + Acting)** loop, allowing the LLM to inspect user queries, dynamically select and execute Python tools, evaluate execution outputs, and synthesize accurate responses.

The application includes:
- **Editorial Streamlit Dashboard**: A minimalist, dark-themed UI featuring conversation threads, title generation, chat deletion, and suggestions.
- **REST API Backend**: FastAPI service supporting asynchronous streaming, session history, and tool metadata endpoints.
- **Modern React Frontend**: Clean Vite + React client for headless integrations.
- **Command Line Interfaces**: Terminal runners with CLI memory inspection and LangGraph workflow visualization.

---

## 🏛️ System Architecture

The following diagram illustrates the flow of execution from the client layer through the LangGraph ReAct agent orchestration to the tool execution and LLM inference engine:

```mermaid
flowchart TD
    subgraph Client Layer
        UI[Streamlit Dark Dashboard]
        REACT[React + Vite Frontend]
        CLI[Terminal CLI Runners]
    end

    subgraph API & Session Layer
        FASTAPI[FastAPI Backend /chat]
        SESSIONS[(In-Memory Session Store)]
    end

    subgraph Agent Core [LangGraph ReAct Engine]
        STATE[Conversation State & History]
        DECIDE{Agent Reasoning Step}
        ACTION[Tool Selection & Dispatch]
        OBSERVE[Observation Synthesizer]
    end

    subgraph LLM Inference Layer
        GROQ[Groq Cloud API\nopenai/gpt-oss-120b\nllama-3.3-70b-versatile]
        OLLAMA[Local Ollama Fallback\nllama3.2 / phi3]
    end

    subgraph Tool Execution Engine
        CALC[🧮 Math Calculator\nAST / Sympy Evaluator]
        KB[📖 Tech Knowledge Base\nIndexed Vector & Docs]
        TIME[🕒 Date & Time Tool\nSystem Clock & Timezones]
    end

    UI -->|Session State| STATE
    REACT -->|HTTP / JSON| FASTAPI
    CLI --> STATE
    FASTAPI <--> SESSIONS
    FASTAPI --> STATE

    STATE --> DECIDE
    DECIDE <-->|Prompt / Tool Schema| GROQ
    DECIDE -.->|Offline Mode| OLLAMA

    DECIDE -->|Calls Tool| ACTION
    ACTION --> CALC
    ACTION --> KB
    ACTION --> TIME

    CALC -->|Result| OBSERVE
    KB -->|Doc Snippet| OBSERVE
    TIME -->|Timestamp| OBSERVE

    OBSERVE -->|Update State| STATE
    DECIDE -->|Final Response| UI
    DECIDE -->|JSON Payload| FASTAPI
```

### Workflow Execution Details:
1. **User Request**: The user submits a query through the Streamlit interface or API.
2. **Context Compilation**: Previous conversation history is retrieved from session state and formatted as LangChain `HumanMessage` and `AIMessage` objects.
3. **Reasoning & Tool Call**: The agent invokes Groq's high-speed inference engine equipped with tool schemas.
4. **Tool Execution**: If a calculation, technical documentation lookup, or current time is needed, the respective Python tool executes safely in an isolated environment.
5. **Observation & Synthesis**: The tool's output is injected into the agent scratchpad, producing a verified final response.

---

## 🛠️ Built-in Tools

| Tool | Capability | Example Queries |
| :--- | :--- | :--- |
| **🧮 Calculator** | Evaluates mathematical expressions, powers, roots, and equations | `"sqrt(144) + 25*3"`, `"2**16 - 1024"` |
| **📖 Knowledge Base** | Retrieves documentation for frameworks, architectures, and libraries | `"What is LangGraph?"`, `"Explain ReAct prompting"` |
| **🕒 Date & Time** | Fetches the current system time, calendar date, and timestamps | `"What day is it today?"`, `"Current UTC time"` |

---

## 📁 Repository Structure

```text
Multi-Tool-LLM-Agent/
├── assets/
│   └── dashboard.png             # UI preview screenshot
├── backend/
│   └── api.py                    # FastAPI server with session & tool endpoints
├── frontend/
│   ├── src/                      # React frontend components and views
│   └── package.json              # Frontend dependencies
├── tools/
│   ├── calculator.py             # Math expression evaluator
│   ├── datetime_tool.py          # Real-time clock and calendar utility
│   └── knowledge_base.py         # Technical documentation lookup
├── tests/
│   └── test_tools.py             # Pytest suite for tool verification
├── .streamlit/
│   └── config.toml               # Streamlit theme and server configuration
├── .env.example                  # Environment template
├── agent.py                      # Basic CLI agent
├── agent_langgraph.py            # LangGraph ReAct workflow runner
├── agent_with_memory.py          # Memory-enabled CLI runner
├── app.py                        # Streamlit dark editorial dashboard
├── config.py                     # Centralized environment & secrets loader
├── requirements.txt              # Python production dependencies
└── setup.py                      # Environment & dependency verification script
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- [Groq API Key](https://console.groq.com/keys) (Free tier available)
- *(Optional)* [Ollama](https://ollama.com/) if running fully local models

### 2. Clone and Install
```bash
git clone https://github.com/syedaftab-dev/Multi-Tool-LLM-Agent.git
cd Multi-Tool-LLM-Agent

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `.env` with your API credentials:
```env
# Provider: "groq" (recommended) or "ollama"
LLM_PROVIDER=groq

# Groq Configuration
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Optional Local Fallback
OLLAMA_MODEL=phi3
OLLAMA_BASE_URL=http://localhost:11434

# Hyperparameters
TEMPERATURE=0.1
MAX_TOKENS=1024
```

### 4. Verify Installation
Run the automated environment check:
```bash
python setup.py
```

---

## 💻 Running the Interfaces

### 🌟 Streamlit Dashboard (Recommended)
Launch the dark-themed editorial chat UI:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### ⚡ FastAPI Backend
Run the high-performance REST API:
```bash
uvicorn backend.api:app --reload --port 8000
```
Interactive Swagger docs will be available at `http://localhost:8000/docs`.

**Key Endpoints:**
- `GET /health` — Service health and active LLM provider info
- `GET /tools` — List registered tools and signatures
- `POST /chat` — Send a message within a session
- `GET /sessions` — List active sessions
- `DELETE /sessions/{session_id}` — Clear a session

### ⚛️ React + Vite Frontend
```bash
cd frontend
npm install
npm run dev
```

### 🖥️ CLI Agent
```bash
# Basic tool calling
python agent.py

# Memory-enabled conversational CLI
python agent_with_memory.py

# LangGraph compiled state graph
python agent_langgraph.py
```

---

## 🧪 Testing

Run automated unit tests to verify tool accuracy:
```bash
python -m pytest tests -v
```

---

## ☁️ Deployment

### Streamlit Community Cloud (1-Click Free Deploy)
1. Fork or push this repository to your GitHub account.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and select **New app**.
3. Choose repository `syedaftab-dev/Multi-Tool-LLM-Agent`, branch `main`, and main file `app.py`.
4. Under **Advanced settings... -> Secrets**, add:
   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   GROQ_MODEL = "openai/gpt-oss-120b"
   ```
5. Click **Deploy!**

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
