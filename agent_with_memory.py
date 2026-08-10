"""
Agent with Memory — Step 2 from the reference article.

An enhanced ReAct agent with conversation memory and multiple
tools (calculator, knowledge base, datetime). The agent remembers
previous messages within the same session.

Usage:
    python agent_with_memory.py

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

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE
from tools import calculator, knowledge_lookup, get_current_datetime

console = Console(force_terminal=True)


def create_agent_with_memory():
    """Create a ReAct agent with conversation memory and multiple tools."""

    # ── Connect to the local Ollama model ────────────────────
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )

    # ── Register all tools ───────────────────────────────────
    tools = [calculator, knowledge_lookup, get_current_datetime]

    # ── Memory for conversation persistence ──────────────────
    memory = MemorySaver()

    # ── System prompt for better behavior ────────────────────
    system_message = (
        "You are a helpful AI assistant running locally. "
        "You have access to tools: a calculator for math, "
        "a knowledge base for tech/programming topics, and "
        "a datetime tool for the current date and time. "
        "Always use the appropriate tool when needed rather "
        "than guessing. Be concise and helpful."
    )

    # ── Create the ReAct agent with memory ───────────────────
    agent = create_react_agent(
        llm,
        tools,
        checkpointer=memory,
        prompt=system_message,
    )

    return agent


def display_tools_table():
    """Display a table of available tools."""
    table = Table(title="Available Tools", border_style="cyan")
    table.add_column("Tool", style="bold cyan")
    table.add_column("Description", style="white")

    table.add_row("Calculator", "Evaluate math expressions (e.g., '2 + 3 * 4', 'sqrt(144)')")
    table.add_row("Knowledge Base", "Look up tech topics (e.g., 'python', 'langchain', 'react')")
    table.add_row("DateTime", "Get current date, time, or day of the week")

    console.print(table)


def main():
    """Run the agent with memory in an interactive CLI loop."""

    console.print(
        Panel(
            "[bold magenta]AI Agent with Memory[/bold magenta]\n"
            f"[dim]Model: {OLLAMA_MODEL} | Tools: 3 | Memory: Enabled[/dim]\n"
            "[dim]Type 'quit' to stop, 'tools' to see available tools,[/dim]\n"
            "[dim]'clear' to reset conversation memory.[/dim]",
            border_style="magenta",
            expand=False,
        )
    )

    display_tools_table()

    agent = create_agent_with_memory()
    thread_id = "session-001"
    config = {"configurable": {"thread_id": thread_id}}

    turn_count = 0

    while True:
        try:
            user_input = console.input("\n[bold green]You > [/bold green]")
        except (EOFError, KeyboardInterrupt):
            break

        stripped = user_input.strip().lower()

        if stripped in ("quit", "exit", "/bye"):
            console.print("[dim]Goodbye![/dim]")
            break

        if stripped == "tools":
            display_tools_table()
            continue

        if stripped == "clear":
            # Reset by creating a new agent instance
            agent = create_agent_with_memory()
            turn_count = 0
            console.print("[yellow]Conversation memory cleared.[/yellow]")
            continue

        if not user_input.strip():
            continue

        turn_count += 1
        console.print(f"[dim]Thinking... (turn {turn_count})[/dim]")

        try:
            # Invoke the agent with memory
            result = agent.invoke(
                {"messages": [("human", user_input)]},
                config=config,
            )

            # Extract the final response
            final_message = result["messages"][-1].content
            console.print(
                Panel(
                    Markdown(final_message),
                    title=f"[bold magenta]Agent (turn {turn_count})[/bold magenta]",
                    border_style="blue",
                )
            )

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
