"""
Advanced LangGraph Agent — Full graph-based agent workflow.

Demonstrates building an agent using LangGraph's explicit graph API
with separate agent and tool nodes, conditional edges, and streaming.

Usage:
    python agent_langgraph.py

Prerequisites:
    1. Ollama installed and running (ollama serve)
    2. A model pulled (ollama pull phi3)
"""

import sys
import os

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Annotated

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from typing_extensions import TypedDict

from config import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE
from tools import calculator, knowledge_lookup, get_current_datetime

console = Console(force_terminal=True)


# ── State Definition ─────────────────────────────────────────
class AgentState(TypedDict):
    """The state that flows through the agent graph."""
    messages: Annotated[list, add_messages]


# ── Build the Graph ──────────────────────────────────────────
def build_agent_graph():
    """
    Build a LangGraph agent with explicit nodes and edges.

    Graph structure:
        START → agent → (tools_condition) → tool_node → agent
                     └→ END (if no tool call)
    """

    # ── LLM with tool binding ────────────────────────────────
    tools = [calculator, knowledge_lookup, get_current_datetime]

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )
    llm_with_tools = llm.bind_tools(tools)

    # ── System prompt ────────────────────────────────────────
    system_msg = SystemMessage(
        content=(
            "You are a helpful AI assistant running locally via Ollama. "
            "You have tools for calculations, knowledge lookups, and "
            "getting the current date/time. Use them when appropriate. "
            "Be concise, accurate, and friendly."
        )
    )

    # ── Agent Node ───────────────────────────────────────────
    def agent_node(state: AgentState) -> AgentState:
        """The 'brain' — call the LLM to decide what to do next."""
        messages = [system_msg] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # ── Tool Node (pre-built) ────────────────────────────────
    tool_node = ToolNode(tools)

    # ── Assemble the Graph ───────────────────────────────────
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    # Compile with memory
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def main():
    """Run the LangGraph agent in an interactive CLI loop."""

    console.print(
        Panel(
            "[bold yellow]LangGraph Agent[/bold yellow]\n"
            f"[dim]Model: {OLLAMA_MODEL} | Architecture: Graph-based[/dim]\n"
            "[dim]Type 'quit' to stop, 'graph' to see the structure.[/dim]",
            border_style="yellow",
            expand=False,
        )
    )

    agent = build_agent_graph()
    thread_id = "langgraph-session-001"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            user_input = console.input("\n[bold green]You > [/bold green]")
        except (EOFError, KeyboardInterrupt):
            break

        stripped = user_input.strip().lower()

        if stripped in ("quit", "exit", "/bye"):
            console.print("[dim]Goodbye![/dim]")
            break

        if stripped == "graph":
            console.print(
                Panel(
                    "START -> [cyan]agent[/cyan] -> "
                    "(tool needed?) -> [yellow]tools[/yellow] -> "
                    "[cyan]agent[/cyan] -> ... -> END",
                    title="Graph Structure",
                    border_style="yellow",
                )
            )
            continue

        if not user_input.strip():
            continue

        console.print("[dim]Processing through graph...[/dim]")

        try:
            # Stream events from the graph
            final_content = ""
            for event in agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="values",
            ):
                # Get the last message from the stream
                last_msg = event["messages"][-1]
                final_content = last_msg.content

            if final_content:
                console.print(
                    Panel(
                        Markdown(final_content),
                        title="[bold yellow]Agent[/bold yellow]",
                        border_style="blue",
                    )
                )

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
