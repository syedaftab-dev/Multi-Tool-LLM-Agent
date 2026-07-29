"""
Central configuration for the Basic Agent project.
Loads settings from .env and provides typed access.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Ollama Settings ──────────────────────────────────────────
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi3")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))

# ── Agent Settings ───────────────────────────────────────────
AGENT_MAX_ITERATIONS: int = 10          # Max reasoning steps per query
AGENT_VERBOSE: bool = True              # Print agent's thought process
MEMORY_KEY: str = "chat_history"        # Key for conversation memory

# ── Knowledge Base ───────────────────────────────────────────
KNOWLEDGE_BASE: dict[str, str] = {
    "python": (
        "Python is a high-level, interpreted programming language created by Guido van Rossum "
        "and first released in 1991. It emphasizes code readability with its use of significant "
        "indentation. Python supports multiple programming paradigms including procedural, "
        "object-oriented, and functional programming. It has a large standard library and a "
        "massive ecosystem of third-party packages (pip). Common use cases include web development "
        "(Django, Flask), data science (pandas, NumPy), machine learning (scikit-learn, TensorFlow), "
        "automation, and scripting. Python is one of the most popular languages in the world."
    ),
    "langchain": (
        "LangChain is an open-source framework for building applications powered by language models. "
        "Created by Harrison Chase in 2022, it provides modular components for: (1) Prompt Templates "
        "for managing and optimizing prompts, (2) Chains for linking multiple LLM calls together, "
        "(3) Agents that use LLMs to decide which tools to call, (4) Memory modules for maintaining "
        "conversation context, and (5) Retrieval systems for connecting LLMs to external data. "
        "LangChain supports integrations with OpenAI, Anthropic, Ollama, and many other providers. "
        "It is written in Python and JavaScript/TypeScript."
    ),
    "ollama": (
        "Ollama is a free, open-source tool that allows you to download and run large language models "
        "locally on your own machine. It supports models like Llama 3, Mistral, Phi-3, Gemma, and many "
        "others. Ollama provides a simple CLI (e.g., 'ollama pull llama3.2', 'ollama run llama3.2') and "
        "a REST API on port 11434 for programmatic access. Key benefits include full data privacy "
        "(nothing leaves your machine), no API costs, and offline capability. It runs on macOS, "
        "Linux, and Windows."
    ),
    "react": (
        "ReAct (Reasoning + Acting) is a prompting pattern for AI agents introduced by Yao et al. "
        "in 2022. The pattern works in a loop: (1) The LLM REASONS about what to do next, "
        "(2) it ACTS by calling a tool or function, (3) it OBSERVES the result, and (4) it repeats "
        "until it has a final answer. This approach is more reliable than pure chain-of-thought "
        "because the agent can ground its reasoning in real tool outputs rather than hallucinating. "
        "ReAct is the default pattern used by LangChain and LangGraph agents."
    ),
    "langgraph": (
        "LangGraph is an extension of LangChain for building stateful, multi-step agent workflows "
        "using a graph-based architecture. Instead of simple linear chains, LangGraph uses StateGraph "
        "with nodes (functions) and edges (transitions) to define complex agent logic. It supports "
        "features like conditional branching, loops, human-in-the-loop, and persistence via "
        "checkpointers. LangGraph is particularly useful for building agents that need to maintain "
        "state across multiple interactions or follow complex decision trees."
    ),
    "agent": (
        "An AI agent is a program that uses a language model as its reasoning engine to think, "
        "plan, make decisions, and take actions to complete a goal. Unlike simple chatbots that "
        "only generate text, agents can use tools (calculators, APIs, databases), maintain memory "
        "across conversations, and break complex tasks into steps. Popular frameworks for building "
        "agents include LangChain, LangGraph, CrewAI, and AutoGen."
    ),
    "slm": (
        "Small Language Models (SLMs) are compact AI models typically with 1-13 billion parameters, "
        "designed to run on consumer hardware like laptops and desktops. Examples include Microsoft's "
        "Phi-3 (3.8B), Meta's Llama 3.2 (3B), and Google's Gemma 2 (2B). SLMs offer advantages like "
        "low latency, full privacy, no API costs, and offline usage. While less capable than large "
        "models (100B+), SLMs are often sufficient for specific tasks like code generation, "
        "summarization, and tool-calling agents."
    ),
    "phi3": (
        "Phi-3 is a family of small language models developed by Microsoft Research. The smallest "
        "variant, Phi-3 Mini, has 3.8 billion parameters and was trained on a curated dataset of "
        "textbooks and synthetic data. Phi-3 is known for strong reasoning and coding capabilities "
        "relative to its size. However, it does not support tool-calling APIs, which limits its "
        "use in agent frameworks that rely on structured function calling."
    ),
    "transformer": (
        "A transformer is a deep learning architecture introduced in the 2017 paper 'Attention Is "
        "All You Need' by Vaswani et al. It is based on self-attention mechanisms that allow the "
        "model to weigh the importance of different parts of the input. Transformers replaced "
        "recurrent neural networks (RNNs) for most NLP tasks and form the backbone of all modern "
        "language models including GPT, BERT, Llama, and Gemini. Key components include multi-head "
        "attention, positional encoding, and feed-forward layers."
    ),
    "rag": (
        "Retrieval-Augmented Generation (RAG) is a technique that combines a retrieval system "
        "(like a vector database) with a language model to provide grounded, factual responses. "
        "Instead of relying solely on the LLM's training data, RAG first searches a knowledge base "
        "for relevant documents, then passes them as context to the LLM. This reduces hallucinations "
        "and allows the model to answer questions about private or recent data. Popular vector "
        "databases for RAG include Pinecone, Weaviate, ChromaDB, and FAISS."
    ),
    "fastapi": (
        "FastAPI is a modern, high-performance Python web framework for building APIs. Created by "
        "Sebastian Ramirez, it is built on top of Starlette (for async web handling) and Pydantic "
        "(for data validation). Key features include automatic OpenAPI/Swagger documentation, "
        "type-safe request/response models, async/await support, and dependency injection. "
        "FastAPI is one of the fastest Python frameworks available and is widely used for building "
        "backend services and microservices."
    ),
    "docker": (
        "Docker is a platform for developing, shipping, and running applications inside containers. "
        "Containers are lightweight, isolated environments that package an application with all its "
        "dependencies, ensuring it runs consistently across different machines. Docker uses images "
        "(blueprints) and containers (running instances). Key commands include docker build, "
        "docker run, and docker compose. Docker is essential for modern DevOps and cloud deployment."
    ),
}
