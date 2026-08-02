"""
Knowledge Base Tool — Looks up topics from a local knowledge dictionary.

Provides the agent with a simple, deterministic way to retrieve
factual definitions for known topics. Includes alias support and
fuzzy matching to handle common misspellings.
"""

from langchain_core.tools import tool
from config import KNOWLEDGE_BASE


# Common aliases and misspellings → canonical key
ALIASES: dict[str, str] = {
    "lang chain": "langchain",
    "lang-chain": "langchain",
    "langraph": "langgraph",
    "lang graph": "langgraph",
    "lang-graph": "langgraph",
    "reactjs": "react",
    "react.js": "react",
    "react js": "react",
    "phi-3": "phi3",
    "phi 3": "phi3",
    "llama": "slm",
    "llama3": "slm",
    "llama 3": "slm",
    "small language model": "slm",
    "fast api": "fastapi",
    "fast-api": "fastapi",
    "retrieval augmented generation": "rag",
}


def _similarity(a: str, b: str) -> float:
    """Simple character-level similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    # Count matching characters in order (longest common subsequence approx)
    matches = sum(1 for ca, cb in zip(a, b) if ca == cb)
    return matches / max(len(a), len(b))


@tool
def knowledge_lookup(topic: str) -> str:
    """Look up a topic in the local knowledge base.

    Use this tool when someone asks about a programming concept,
    framework, or technology. Returns a concise definition if the
    topic is found, or a helpful message if not.

    Args:
        topic: The topic to look up (e.g., 'python', 'langchain', 'react').

    Returns:
        A definition string or a 'not found' message with available topics.
    """
    # Normalize the query
    key = topic.strip().lower()

    # 1. Exact match
    if key in KNOWLEDGE_BASE:
        return f"{topic.title()}: {KNOWLEDGE_BASE[key]}"

    # 2. Alias match (handles misspellings like "langraph" → "langgraph")
    if key in ALIASES:
        canonical = ALIASES[key]
        if canonical in KNOWLEDGE_BASE:
            return f"{canonical.title()}: {KNOWLEDGE_BASE[canonical]}"

    # 3. Substring match
    partial_matches = [k for k in KNOWLEDGE_BASE if key in k or k in key]
    if partial_matches:
        results = "\n".join(
            f"  - {k.title()}: {KNOWLEDGE_BASE[k]}" for k in partial_matches
        )
        return f"Found related topics:\n{results}"

    # 4. Similarity match (catches close typos like "pythn" → "python")
    best_match = None
    best_score = 0.0
    for kb_key in KNOWLEDGE_BASE:
        score = _similarity(key, kb_key)
        if score > best_score:
            best_score = score
            best_match = kb_key

    if best_match and best_score >= 0.6:
        return (
            f"Did you mean '{best_match}'? "
            f"{best_match.title()}: {KNOWLEDGE_BASE[best_match]}"
        )

    available = ", ".join(sorted(KNOWLEDGE_BASE.keys()))
    return (
        f"Topic '{topic}' not found in the knowledge base.\n"
        f"Available topics: {available}"
    )
