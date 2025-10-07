"""Main UI application for OpenGov Early Mathematics."""

import asyncio
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Select
from rich.table import Table

from opengov_earlymathematics.ai.tutor import AITutor
from opengov_earlymathematics.config import settings
from opengov_earlymathematics.core.models import Student
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer()


class MathLearningApp:
    """Interactive mathematics learning application."""

    def __init__(self):
        """Initialize the learning app."""
        self.current_student: Optional[Student] = None
        self.ai_tutor: Optional[AITutor] = None
        self.current_session: Optional[Dict[str, Any]] = None
        self.learning_history: List[Dict[str, Any]] = []

    def run(self):
        """Run the main application."""
        console.print(
            Panel.fit(
                "[bold blue]🌟 Welcome to OpenGov Early Mathematics! 🌟[/bold blue]\n\n"
                "An AI-powered learning platform for K-12 mathematics education.",
                title="OpenGov Early Mathematics",
                border_style="blue",
            )
        )

        # Main menu loop
        while True:
            choice = self._show_main_menu()

            if choice == "start_session":
                self._start_learning_session()
            elif choice == "view_progress":
                self._view_progress()
            elif choice == "manage_students":
                self._manage_students()
            elif choice == "settings":
                self._show_settings()
            elif choice == "exit":
                self._exit_app()
                break

    def _show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        console.clear()

        table = Table(title="Main Menu", show_header=False, box=None)
        table.add_column("Option", style="cyan", width=20)
        table.add_column("Description", style="white")

        table.add_row("1", "Start Learning Session")
        table.add_row("2", "View Progress")
        table.add_row("3", "Manage Students")
        table.add_row("4", "Settings")
        table.add_row("5", "Exit")

        console.print(Panel(table, title="OpenGov Early Mathematics", border_style="blue"))

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"], default="1")

        return {
            "1": "start_session",
            "2": "view_progress",
            "3": "manage_students",
            "4": "settings",
            "5": "exit",
        }[choice]

    def _start_learning_session(self):
        """Start a new learning session."""
        console.clear()

        # Student selection
        if not self.current_student:
            self._select_student()

        if not self.current_student:
            return

        # Topic selection
        topics = [
            "Basic Addition",
            "Basic Subtraction",
            "Multiplication",
            "Division",
            "Fractions",
            "Decimals",
            "Geometry",
            "Algebra Basics",
            "Word Problems",
        ]

        topic = Select.ask("Choose a topic to learn", choices=topics)

        # Initialize AI tutor
        self.ai_tutor = AITutor(self.current_student.id)

        # Start session
        with console.status("[bold green]Starting learning session..."):
            self.current_session = self.ai_tutor.start_session(topic)

        console.print("\n[green]Session started![/green]")
        console.print(f"[blue]Topic:[/blue] {topic}")

        # Learning session loop
        self._run_learning_session()

    def _run_learning_session(self):
        """Run the interactive learning session."""
        while True:
            console.print("\n" + "=" * 50)

            # Show current progress
            if self.learning_history:
                console.print(f"[dim]Problems solved: {len(self.learning_history)}[/dim]")

            # Get user input
            user_input = Prompt.ask("\nWhat would you like to do?", default="ask question")

            if user_input.lower() in ["quit", "exit", "back"]:
                break

            if user_input.lower() in ["help", "hint"]:
                if self.ai_tutor:
                    hint = self.ai_tutor.provide_hint("current")
                    console.print(f"[yellow]💡 Hint:[/yellow] {hint}")
                continue

            if user_input.lower() in ["explain", "concept"]:
                concept = Prompt.ask("What concept would you like explained?")
                if self.ai_tutor:
                    explanation = self.ai_tutor.explain_concept(concept, 8)  # Default grade 8
                    console.print(f"[blue]📚 Explanation:[/blue] {explanation}")
                continue

            # Ask AI tutor for help
            if self.ai_tutor:
                with console.status("[bold green]Thinking..."):
                    response = self.ai_tutor.help_with(user_input)

                console.print(f"\n[green]🤖 AI Tutor:[/green] {response}")

                # Record in history
                self.learning_history.append(
                    {
                        "question": user_input,
                        "response": response,
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                )

    def _select_student(self):
        """Select or create a student."""
        console.print("\n[bold]Student Selection[/bold]")

        # For now, create a demo student
        # In a real app, this would load from database
        student_name = Prompt.ask("Enter your name", default="Demo Student")

        self.current_student = Student(
            id=f"student_{hash(student_name) % 10000}",
            name=student_name,
            grade=8,  # Default grade
            topics_mastered=[],
            current_level="beginner",
        )

        console.print(f"[green]Welcome, {student_name}![/green]")

    def _view_progress(self):
        """View learning progress."""
        console.clear()

        if not self.learning_history:
            console.print("[yellow]No learning history available yet.[/yellow]")
            console.print("Start a learning session to begin tracking progress!")
            Prompt.ask("\nPress Enter to continue")
            return

        # Show progress summary
        table = Table(title="Learning Progress")
        table.add_column("Problems Solved", style="cyan")
        table.add_column("Topics Covered", style="green")
        table.add_column("Time Spent", style="yellow")

        problems_count = len(self.learning_history)
        topics = set()
        total_time = sum(
            entry.get("time_spent", 0) for entry in self.learning_history if "time_spent" in entry
        )

        table.add_row(str(problems_count), str(len(topics)), f"{total_time:.1f} minutes")

        console.print(Panel(table, border_style="blue"))

        # Show recent activity
        if self.learning_history:
            recent_table = Table(title="Recent Activity")
            recent_table.add_column("Question", style="white", width=30)
            recent_table.add_column("Response", style="green", width=30)

            for entry in self.learning_history[-5:]:  # Last 5 entries
                question = entry.get("question", "")[:50] + "..."
                response = entry.get("response", "")[:50] + "..."
                recent_table.add_row(question, response)

            console.print(Panel(recent_table, border_style="green"))

        Prompt.ask("\nPress Enter to continue")

    def _manage_students(self):
        """Manage student profiles."""
        console.clear()
        console.print("[bold]Student Management[/bold]")
        console.print("This feature is coming soon!")
        console.print("For now, students are managed automatically.")
        Prompt.ask("\nPress Enter to continue")

    def _show_settings(self):
        """Show application settings."""
        console.clear()

        table = Table(title="Application Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("OpenAI Model", settings.openai_model)
        table.add_row("Max Tokens", str(settings.openai_max_tokens))
        table.add_row("Temperature", str(settings.openai_temperature))
        table.add_row("Debug Mode", str(settings.debug))

        console.print(Panel(table, border_style="blue"))

        Prompt.ask("\nPress Enter to continue")

    def _exit_app(self):
        """Exit the application."""
        console.print("\n[bold blue]Thank you for using OpenGov Early Mathematics![/bold blue]")
        console.print("[green]Keep learning and exploring! 🌟[/green]")


@app.command()
def tui():
    """Launch the terminal user interface."""
    try:
        math_app = MathLearningApp()
        math_app.run()
    except KeyboardInterrupt:
        console.print("\n[blue]Goodbye! 👋[/blue]")
    except Exception as e:
        logger.error(f"Error in TUI: {e}")
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def serve():
    """Start the API server."""
    console.print("[green]Starting API server...[/green]")
    console.print("API server functionality coming soon!")
    console.print(
        "Use 'uv run python -m opengov_earlymathematics.ui.app tui' for the interactive interface."
    )


if __name__ == "__main__":
    app()
