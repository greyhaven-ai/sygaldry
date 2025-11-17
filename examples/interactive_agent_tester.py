#!/usr/bin/env python3
"""
Interactive Agent Tester for Sygaldry Framework

This script provides an interactive interface to test various Sygaldry agents
with custom inputs and see their responses in real-time.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import traceback

# Add the packages directory to the path (from examples directory)
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sygaldry_registry"))

# Import rich for nice terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.columns import Columns
    from rich.tree import Tree
    from rich import print as rprint
except ImportError:
    print("Please install rich: pip install rich")
    sys.exit(1)

console = Console()

# Agent configurations with their required functions
AGENTS = {
    "1": {
        "name": "Text Summarization Agent",
        "module": "components.agents.text_summarization",
        "functions": ["summarize_text", "quick_summary", "executive_brief", "multi_style_summary"],
        "description": "Advanced text summarization with multiple styles and progressive summarization",
        "examples": {
            "summarize_text": {
                "description": "Full summarization with analysis",
                "params": {"text": "Your long text here...", "style": "technical", "max_length": 200}
            },
            "quick_summary": {
                "description": "Quick one-paragraph summary",
                "params": {"text": "Your text here..."}
            }
        }
    },
    "2": {
        "name": "Hallucination Detector Agent",
        "module": "components.agents.hallucination_detector",
        "functions": ["detect_hallucinations"],
        "description": "AI-powered hallucination detection that verifies factual claims",
        "examples": {
            "detect_hallucinations": {
                "description": "Detect hallucinations in text",
                "params": {"text": "The Eiffel Tower was built in 1989 in London."}
            }
        }
    },
    "3": {
        "name": "Sentiment Analysis Agent",
        "module": "components.agents.sentiment_analysis",
        "functions": ["analyze_sentiment"],
        "description": "Multi-dimensional sentiment analysis with emotion detection",
        "examples": {
            "analyze_sentiment": {
                "description": "Analyze sentiment and emotions",
                "params": {"text": "I absolutely love this product! It exceeded all my expectations."}
            }
        }
    },
    "4": {
        "name": "Code Review Agent",
        "module": "components.agents.code_review",
        "functions": ["review_code"],
        "description": "Automated code review with security checks and best practices",
        "examples": {
            "review_code": {
                "description": "Review Python code",
                "params": {
                    "code": "def add(a, b):\n    return a + b",
                    "language": "python",
                    "focus_areas": ["security", "performance", "style"]
                }
            }
        }
    },
    "5": {
        "name": "PII Scrubbing Agent",
        "module": "components.agents.pii_scrubbing",
        "functions": ["scrub_pii"],
        "description": "Detect and remove Personally Identifiable Information from text",
        "examples": {
            "scrub_pii": {
                "description": "Remove PII from text",
                "params": {
                    "text": "John Doe's email is john@example.com and his SSN is 123-45-6789",
                    "scrubbing_method": "mask"
                }
            }
        }
    },
    "6": {
        "name": "Contract Analysis Agent",
        "module": "components.agents.contract_analysis",
        "functions": ["analyze_contract"],
        "description": "Legal document analysis for risks, obligations, and key terms",
        "examples": {
            "analyze_contract": {
                "description": "Analyze a contract",
                "params": {
                    "contract_text": "This agreement between Party A and Party B...",
                    "contract_type": "service",
                    "focus_areas": ["payment_terms", "termination", "liability"]
                }
            }
        }
    },
    "7": {
        "name": "Financial Statement Analyzer",
        "module": "components.agents.financial_statement_analyzer",
        "functions": ["analyze_financial_statement"],
        "description": "Analyze financial reports and provide investment insights",
        "examples": {
            "analyze_financial_statement": {
                "description": "Analyze financial data",
                "params": {
                    "statement_text": "Revenue: $1M, Expenses: $800K, Assets: $5M",
                    "statement_type": "income_statement",
                    "analysis_depth": "comprehensive"
                }
            }
        }
    },
    "8": {
        "name": "Bug Triage Agent",
        "module": "components.agents.bug_triage",
        "functions": ["triage_bug"],
        "description": "Bug report analysis and classification",
        "examples": {
            "triage_bug": {
                "description": "Triage a bug report",
                "params": {
                    "title": "App crashes on startup",
                    "description": "The application crashes when trying to open a large file",
                    "environment": "Production, Windows 10, 8GB RAM"
                }
            }
        }
    },
    "9": {
        "name": "Task Prioritization Agent",
        "module": "components.agents.task_prioritization",
        "functions": ["prioritize_tasks"],
        "description": "Task prioritization using Eisenhower matrix",
        "examples": {
            "prioritize_tasks": {
                "description": "Prioritize a list of tasks",
                "params": {
                    "tasks": [
                        "Fix critical production bug",
                        "Update documentation",
                        "Attend team meeting",
                        "Research new framework"
                    ]
                }
            }
        }
    },
    "10": {
        "name": "Content Moderation Agent",
        "module": "components.agents.content_moderation",
        "functions": ["moderate_content"],
        "description": "Detect harmful content, hate speech, and misinformation",
        "examples": {
            "moderate_content": {
                "description": "Moderate user content",
                "params": {
                    "content": "This is a sample message to moderate",
                    "platform": "forum"
                }
            }
        }
    }
}


class AgentTester:
    """Interactive agent testing interface."""

    def __init__(self):
        self.console = console
        self.current_agent = None
        self.test_history = []

    def display_welcome(self):
        """Display welcome message."""
        welcome_text = """
# Sygaldry Interactive Agent Tester

Welcome to the Sygaldry framework interactive agent testing environment!
This tool allows you to test various AI agents with custom inputs and see their responses in real-time.

## Features:
- Test agents interactively with custom inputs
- View example usage for each agent
- See detailed responses with structured output
- Test history tracking
- Easy navigation between agents
        """
        self.console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="cyan"))

    def display_agents_menu(self):
        """Display available agents in a nice table."""
        table = Table(title="Available Agents", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Agent Name", style="green", width=30)
        table.add_column("Description", style="yellow")

        for agent_id, agent_info in AGENTS.items():
            table.add_row(agent_id, agent_info["name"], agent_info["description"])

        self.console.print(table)
        self.console.print("\n[bold cyan]Options:[/bold cyan]")
        self.console.print("  Enter agent ID (1-10) to select an agent")
        self.console.print("  Enter 'h' to view test history")
        self.console.print("  Enter 'q' to quit")

    async def load_agent(self, agent_id: str):
        """Load the selected agent."""
        if agent_id not in AGENTS:
            self.console.print("[red]Invalid agent ID![/red]")
            return False

        agent_info = AGENTS[agent_id]
        self.console.print(f"\n[cyan]Loading {agent_info['name']}...[/cyan]")

        try:
            # Import the agent module
            module = __import__(agent_info["module"], fromlist=agent_info["functions"])
            self.current_agent = {
                "info": agent_info,
                "module": module,
                "functions": {func: getattr(module, func) for func in agent_info["functions"]}
            }
            self.console.print(f"[green]✓ {agent_info['name']} loaded successfully![/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Error loading agent: {e}[/red]")
            self.console.print(f"[yellow]Make sure you have installed all dependencies:[/yellow]")
            self.console.print("[yellow]pip install mirascope pydantic rich[/yellow]")
            return False

    def display_agent_menu(self):
        """Display menu for the current agent."""
        agent_info = self.current_agent["info"]

        # Display agent header
        self.console.print(Panel(
            f"[bold green]{agent_info['name']}[/bold green]\n\n{agent_info['description']}",
            title="Current Agent",
            border_style="green"
        ))

        # Display available functions
        self.console.print("\n[bold cyan]Available Functions:[/bold cyan]")
        for i, func_name in enumerate(agent_info["functions"], 1):
            example = agent_info.get("examples", {}).get(func_name, {})
            desc = example.get("description", "No description available")
            self.console.print(f"  {i}. [green]{func_name}[/green] - {desc}")

        self.console.print("\n[bold cyan]Options:[/bold cyan]")
        self.console.print("  Enter function number to test it")
        self.console.print("  Enter 'e' to view examples")
        self.console.print("  Enter 'b' to go back to agent selection")
        self.console.print("  Enter 'q' to quit")

    async def test_function(self, func_name: str):
        """Test a specific function of the current agent."""
        agent_info = self.current_agent["info"]
        func = self.current_agent["functions"][func_name]

        # Display function info
        self.console.print(f"\n[bold cyan]Testing: {func_name}[/bold cyan]")

        # Show example if available
        example = agent_info.get("examples", {}).get(func_name, {})
        if example:
            self.console.print("\n[yellow]Example parameters:[/yellow]")
            self.console.print(Syntax(json.dumps(example["params"], indent=2), "json"))

        # Get input method
        input_method = Prompt.ask(
            "\nHow would you like to provide input?",
            choices=["custom", "example", "back"],
            default="custom"
        )

        if input_method == "back":
            return
        elif input_method == "example" and example:
            params = example["params"]
        else:
            # Get custom input
            params = {}
            self.console.print("\n[cyan]Enter parameters (leave empty to skip optional params):[/cyan]")

            if "text" in str(example.get("params", {})):
                text = Prompt.ask("Enter text", default="")
                if text:
                    params["text"] = text

            # Ask for additional common parameters based on function name
            if "summarize" in func_name:
                style = Prompt.ask("Style", choices=["technical", "executive", "simple", "academic", "journalistic"], default="technical")
                params["style"] = style
                max_length = Prompt.ask("Max length (words)", default="200")
                params["max_length"] = int(max_length)
            elif "code" in func_name:
                code = Prompt.ask("Enter code (or 'file' to load from file)")
                if code == "file":
                    filepath = Prompt.ask("Enter file path")
                    with open(filepath, "r") as f:
                        params["code"] = f.read()
                else:
                    params["code"] = code
                language = Prompt.ask("Language", default="python")
                params["language"] = language

        # Run the function
        self.console.print("\n[cyan]Running agent function...[/cyan]")
        start_time = datetime.now()

        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(func):
                result = await func(**params)
            else:
                result = func(**params)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Display results
            self.console.print(f"\n[green]✓ Function completed in {duration:.2f} seconds[/green]")
            self.console.print("\n[bold cyan]Result:[/bold cyan]")

            # Format the result based on its type
            if hasattr(result, "model_dump"):
                # Pydantic model
                result_dict = result.model_dump()
                self.console.print(Syntax(json.dumps(result_dict, indent=2), "json"))
            elif isinstance(result, dict):
                self.console.print(Syntax(json.dumps(result, indent=2), "json"))
            elif isinstance(result, str):
                self.console.print(Panel(result, border_style="green"))
            else:
                self.console.print(result)

            # Save to history
            self.test_history.append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent_info["name"],
                "function": func_name,
                "params": params,
                "duration": duration,
                "success": True
            })

        except Exception as e:
            self.console.print(f"\n[red]Error running function: {e}[/red]")
            self.console.print("[yellow]Stack trace:[/yellow]")
            self.console.print(traceback.format_exc())

            # Save error to history
            self.test_history.append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent_info["name"],
                "function": func_name,
                "params": params,
                "error": str(e),
                "success": False
            })

    def display_examples(self):
        """Display examples for the current agent."""
        agent_info = self.current_agent["info"]
        examples = agent_info.get("examples", {})

        if not examples:
            self.console.print("[yellow]No examples available for this agent.[/yellow]")
            return

        for func_name, example in examples.items():
            self.console.print(f"\n[bold green]{func_name}[/bold green]")
            self.console.print(f"  {example['description']}")
            self.console.print("\n  [cyan]Parameters:[/cyan]")
            self.console.print(Syntax(json.dumps(example["params"], indent=4), "json"))

    def display_history(self):
        """Display test history."""
        if not self.test_history:
            self.console.print("[yellow]No test history yet.[/yellow]")
            return

        table = Table(title="Test History", show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan")
        table.add_column("Agent", style="green")
        table.add_column("Function", style="yellow")
        table.add_column("Status", style="white")
        table.add_column("Duration", style="blue")

        for test in self.test_history[-10:]:  # Show last 10 tests
            time_str = datetime.fromisoformat(test["timestamp"]).strftime("%H:%M:%S")
            status = "[green]✓[/green]" if test["success"] else "[red]✗[/red]"
            duration = f"{test.get('duration', 0):.2f}s" if test["success"] else "N/A"

            table.add_row(
                time_str,
                test["agent"][:20],
                test["function"],
                status,
                duration
            )

        self.console.print(table)

    async def run(self):
        """Main run loop."""
        self.display_welcome()

        while True:
            if self.current_agent is None:
                # Agent selection menu
                self.display_agents_menu()
                choice = Prompt.ask("\nEnter your choice").lower()

                if choice == 'q':
                    self.console.print("[cyan]Goodbye![/cyan]")
                    break
                elif choice == 'h':
                    self.display_history()
                    input("\nPress Enter to continue...")
                elif choice in AGENTS:
                    if await self.load_agent(choice):
                        continue
                else:
                    self.console.print("[red]Invalid choice![/red]")

            else:
                # Agent testing menu
                self.display_agent_menu()
                choice = Prompt.ask("\nEnter your choice").lower()

                if choice == 'q':
                    self.console.print("[cyan]Goodbye![/cyan]")
                    break
                elif choice == 'b':
                    self.current_agent = None
                elif choice == 'e':
                    self.display_examples()
                    input("\nPress Enter to continue...")
                elif choice.isdigit():
                    func_idx = int(choice) - 1
                    functions = self.current_agent["info"]["functions"]
                    if 0 <= func_idx < len(functions):
                        await self.test_function(functions[func_idx])
                        input("\nPress Enter to continue...")
                    else:
                        self.console.print("[red]Invalid function number![/red]")
                else:
                    self.console.print("[red]Invalid choice![/red]")


async def main():
    """Main entry point."""
    # Check for API keys
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        console.print(f"[yellow]Warning: Missing API keys: {', '.join(missing_keys)}[/yellow]")
        console.print("[yellow]Some agents may not work without proper API keys.[/yellow]")
        if not Confirm.ask("Continue anyway?"):
            return

    tester = AgentTester()
    await tester.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted by user. Goodbye![/cyan]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        console.print(traceback.format_exc())