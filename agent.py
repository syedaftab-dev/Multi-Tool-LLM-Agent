"""
Basic AI Agent — Step 1 from the reference article.

A simple ReAct agent connected to a local Ollama model with a
single calculator tool. This is the minimal working example.

Usage:
    python agent.py

Prerequisites:
    1. Ollama installed and running (ollama serve)
    2. A model pulled (ollama pull phi3)
"""

import sys
import os

# Fix Windows console encoding for rich/emoji output
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

from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from config import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE
from tools.calculator import calculator

console = Console(force_terminal=True)


def create_basic_agent():
    """Create and return a basic ReAct agent with a calculator tool."""

    # ── Connect to the local Ollama model ────────────────────
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )

    # ── Register tools ───────────────────────────────────────
    tools = [calculator]

    # ── Create the ReAct agent ───────────────────────────────
    # The ReAct pattern: Reason → Act → Observe → Repeat
    agent = create_react_agent(llm, tools)

    return agent


def main():
    """Run the basic agent in an interactive CLI loop."""

    console.print(
        Panel(
            "[bold cyan]Basic AI Agent[/bold cyan]\n"
            f"[dim]Model: {OLLAMA_MODEL} | Tool: Calculator[/dim]\n"
            "[dim]Type 'quit' or 'exit' to stop.[/dim]",
            border_style="cyan",
            expand=False,
        )
    )

    agent = create_basic_agent()

    while True:
        try:
            user_input = console.input("\n[bold green]You > [/bold green]")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.strip().lower() in ("quit", "exit", "/bye"):
            console.print("[dim]Goodbye![/dim]")
            break

        if not user_input.strip():
            continue

        console.print("[dim]Thinking...[/dim]")

        try:
            # Invoke the agent
            result = agent.invoke(
                {"messages": [("human", user_input)]}
            )

            # Extract the final response
            final_message = result["messages"][-1].content
            console.print(
                Panel(
                    Markdown(final_message),
                    title="[bold cyan]Agent[/bold cyan]",
                    border_style="blue",
                )
            )

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
