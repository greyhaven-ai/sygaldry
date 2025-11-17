#!/usr/bin/env python3
"""
Simple Agent Demo for Sygaldry Framework

A straightforward script to demonstrate individual agents.
Run with: python simple_agent_demo.py
"""

import asyncio
import sys
from pathlib import Path
import os

# Add the packages directory to the path (from examples directory)
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sygaldry_registry"))

# Import what we need
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich import print as rprint
except ImportError:
    print("Installing rich for better output...")
    os.system("pip install rich")
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt

console = Console()


async def test_text_summarization():
    """Test the text summarization agent."""
    console.print(Panel("[bold cyan]Text Summarization Agent Demo[/bold cyan]", expand=False))

    try:
        from components.agents.text_summarization import summarize_text, quick_summary

        # Sample text for testing
        sample_text = """
        Artificial Intelligence (AI) has become one of the most transformative technologies of the 21st century.
        From its early beginnings in the 1950s, when computer scientists first began to explore the possibility
        of creating machines that could think and learn like humans, AI has evolved dramatically. Today, AI
        systems power everything from voice assistants on our phones to complex decision-making systems in
        healthcare and finance. Machine learning, a subset of AI, has particularly revolutionized how we
        process and analyze large datasets, enabling computers to identify patterns and make predictions with
        unprecedented accuracy. Deep learning, inspired by the human brain's neural networks, has pushed the
        boundaries even further, achieving remarkable results in image recognition, natural language processing,
        and game playing. As we look to the future, AI continues to present both immense opportunities and
        significant challenges, from ethical considerations about bias and transparency to questions about
        the impact on employment and society as a whole.
        """

        console.print("\n[yellow]Original Text:[/yellow]")
        console.print(Panel(sample_text.strip(), expand=False))

        # Test quick summary
        console.print("\n[cyan]Running quick_summary()...[/cyan]")
        quick_result = quick_summary(sample_text)
        console.print("\n[green]Quick Summary:[/green]")
        if hasattr(quick_result, "summary"):
            console.print(Panel(quick_result.summary, expand=False))
        else:
            console.print(quick_result)

        # Test detailed summarization
        console.print("\n[cyan]Running summarize_text() with 'technical' style...[/cyan]")
        detailed_result = summarize_text(sample_text, style="technical", max_length=100)
        console.print("\n[green]Technical Summary:[/green]")
        if hasattr(detailed_result, "summary"):
            console.print(Panel(detailed_result.summary, expand=False))
            console.print(f"[dim]Confidence Score: {detailed_result.confidence_score:.2f}[/dim]")
            console.print(f"[dim]Word Count: {detailed_result.word_count}[/dim]")
        else:
            console.print(detailed_result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Make sure you have the required API keys set:[/yellow]")
        console.print("export OPENAI_API_KEY='your-key-here'")


async def test_sentiment_analysis():
    """Test the sentiment analysis agent."""
    console.print(Panel("[bold cyan]Sentiment Analysis Agent Demo[/bold cyan]", expand=False))

    try:
        from components.agents.sentiment_analysis import analyze_sentiment

        # Sample texts with different sentiments
        samples = [
            ("I absolutely love this product! It exceeded all my expectations and the customer service was fantastic.", "positive"),
            ("This is the worst experience I've ever had. Completely disappointed and will never buy again.", "negative"),
            ("The product is okay. It works as described but nothing special. Average quality for the price.", "neutral"),
        ]

        for text, expected in samples:
            console.print(f"\n[yellow]Text:[/yellow] {text}")
            console.print(f"[dim]Expected: {expected}[/dim]")

            result = analyze_sentiment(text)

            if hasattr(result, "model_dump"):
                data = result.model_dump()
                console.print(f"[green]Overall Sentiment:[/green] {data.get('overall_sentiment', 'Unknown')}")
                console.print(f"[green]Polarity:[/green] {data.get('polarity', 0):.2f}")
                console.print(f"[green]Subjectivity:[/green] {data.get('subjectivity', 0):.2f}")
                if 'emotions' in data:
                    console.print(f"[green]Emotions:[/green] {', '.join(data['emotions'])}")
            else:
                console.print(result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def test_pii_scrubbing():
    """Test the PII scrubbing agent."""
    console.print(Panel("[bold cyan]PII Scrubbing Agent Demo[/bold cyan]", expand=False))

    try:
        from components.agents.pii_scrubbing import scrub_pii

        # Sample text with PII
        sample_text = """
        Hello, my name is John Smith and I work at Acme Corporation.
        You can reach me at john.smith@example.com or call me at 555-123-4567.
        My social security number is 123-45-6789 and I live at 123 Main St, Anytown, USA.
        """

        console.print("\n[yellow]Original Text (with PII):[/yellow]")
        console.print(Panel(sample_text.strip(), expand=False))

        # Test masking
        console.print("\n[cyan]Running scrub_pii() with 'mask' method...[/cyan]")
        masked_result = scrub_pii(sample_text, scrubbing_method="mask")

        if hasattr(masked_result, "scrubbed_text"):
            console.print("\n[green]Masked Text:[/green]")
            console.print(Panel(masked_result.scrubbed_text, expand=False))
            console.print(f"[dim]PII Found: {len(masked_result.pii_found)} items[/dim]")
            for pii in masked_result.pii_found:
                console.print(f"  - {pii.type}: [red strikethrough]{pii.original_value}[/red strikethrough]")
        else:
            console.print(masked_result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def test_code_review():
    """Test the code review agent."""
    console.print(Panel("[bold cyan]Code Review Agent Demo[/bold cyan]", expand=False))

    try:
        from components.agents.code_review import review_code

        # Sample code to review
        sample_code = """
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    average = total / len(numbers)
    return average

def get_user_data(user_id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    return result
"""

        console.print("\n[yellow]Code to Review:[/yellow]")
        console.print(Panel(sample_code.strip(), expand=False))

        console.print("\n[cyan]Running review_code()...[/cyan]")
        result = review_code(
            code=sample_code,
            language="python",
            focus_areas=["security", "performance", "style", "best_practices"]
        )

        if hasattr(result, "model_dump"):
            data = result.model_dump()
            console.print(f"\n[green]Overall Score:[/green] {data.get('overall_score', 0)}/10")

            if 'issues' in data:
                console.print("\n[yellow]Issues Found:[/yellow]")
                for issue in data['issues']:
                    severity_color = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "dim"}.get(issue.get('severity', 'low'), 'white')
                    console.print(f"  [{severity_color}]• Line {issue.get('line', '?')}: {issue.get('message', '')}[/{severity_color}]")

            if 'suggestions' in data:
                console.print("\n[green]Suggestions:[/green]")
                for suggestion in data['suggestions']:
                    console.print(f"  • {suggestion}")
        else:
            console.print(result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


async def main():
    """Main demo runner."""
    console.print(Panel(Markdown("""
# Sygaldry Agent Demo

This demo will showcase several Sygaldry agents in action.
Each agent will be tested with sample data.

**Note:** You need API keys set as environment variables:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
    """), title="Welcome", expand=False))

    demos = {
        "1": ("Text Summarization", test_text_summarization),
        "2": ("Sentiment Analysis", test_sentiment_analysis),
        "3": ("PII Scrubbing", test_pii_scrubbing),
        "4": ("Code Review", test_code_review),
        "5": ("Run All Demos", None),
    }

    while True:
        console.print("\n[bold cyan]Available Demos:[/bold cyan]")
        for key, (name, _) in demos.items():
            console.print(f"  {key}. {name}")
        console.print("  q. Quit")

        choice = Prompt.ask("\nSelect a demo", default="1")

        if choice.lower() == 'q':
            console.print("[cyan]Goodbye![/cyan]")
            break
        elif choice == "5":
            # Run all demos
            for name, func in demos.items():
                if func is not None:
                    console.print(f"\n{'='*60}")
                    await func()
                    input("\nPress Enter to continue to next demo...")
        elif choice in demos and demos[choice][1] is not None:
            await demos[choice][1]()
            input("\nPress Enter to continue...")
        else:
            console.print("[red]Invalid choice![/red]")


if __name__ == "__main__":
    # Check for at least one API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: No API keys found![/red]")
        console.print("\nPlease set one of the following environment variables:")
        console.print("  export OPENAI_API_KEY='your-openai-key'")
        console.print("  export ANTHROPIC_API_KEY='your-anthropic-key'")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted by user. Goodbye![/cyan]")