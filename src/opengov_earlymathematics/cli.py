"""Command-line interface for OpenGov-EarlyMathematics."""

import typer
from rich.console import Console
from rich.table import Table

from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.problem_engine import MathProblemSolver
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

app = typer.Typer(
    name="opengov-math",
    help="OpenGov-EarlyMathematics CLI",
    add_completion=False,
)


@app.command()
def version():
    """Show version information."""
    console.print("[bold blue]OpenGov-EarlyMathematics[/bold blue]")
    console.print("Version: 0.1.0")
    console.print("AI-powered personalized mathematics education platform")


@app.command()
def curriculum(grade: str = typer.Option(None, help="Filter by grade level")):
    """Show curriculum information."""
    curriculum_manager = Curriculum()

    if grade:
        try:
            from opengov_earlymathematics.core.models import GradeLevel

            grade_level = GradeLevel(grade)
            topics = curriculum_manager.get_topics_for_grade(grade_level)

            console.print(f"[bold]Topics for Grade {grade}:[/bold]")
            for topic in topics:
                console.print(f"• {topic.value}")
        except ValueError:
            console.print(f"[red]Invalid grade level: {grade}[/red]")
    else:
        # Show all grades and topics
        table = Table(title="Mathematics Curriculum")
        table.add_column("Grade", style="cyan")
        table.add_column("Topics", style="magenta")

        for grade in ["K", "1", "2", "3", "4", "5"]:
            try:
                from opengov_earlymathematics.core.models import GradeLevel

                grade_level = GradeLevel(grade)
                topics = curriculum_manager.get_topics_for_grade(grade_level)
                topic_names = [topic.value for topic in topics[:3]]  # Show first 3
                table.add_row(grade, ", ".join(topic_names))
            except ValueError:
                continue

        console.print(table)


@app.command()
def generate_problem(
    topic: str = typer.Option(..., help="Math topic"),
    difficulty: int = typer.Option(1, help="Difficulty level (1-4)"),
    grade: int = typer.Option(3, help="Grade level"),
):
    """Generate a math problem."""
    try:
        solver = MathProblemSolver()
        problem = solver.generate_problem(topic, difficulty, grade)

        console.print("[bold green]Generated Problem:[/bold green]")
        console.print(f"Topic: {problem.topic.value}")
        console.print(f"Grade: {problem.grade_level.value}")
        console.print(f"Difficulty: {problem.difficulty.value}")
        console.print()
        console.print(f"[bold]Question:[/bold] {problem.question}")
        console.print()
        console.print("[bold]Hints:[/bold]")
        for i, hint in enumerate(problem.hints, 1):
            console.print(f"{i}. {hint}")

    except Exception as e:
        console.print(f"[red]Error generating problem: {e}[/red]")


@app.command()
def check_solution(
    problem_id: str = typer.Option(..., help="Problem ID"),
    answer: str = typer.Option(..., help="Student's answer"),
):
    """Check a solution."""
    try:
        solver = MathProblemSolver()
        result = solver.check_solution(problem_id, answer, show_steps=True)

        if result["correct"]:
            console.print("[green]✅ Correct![/green]")
        else:
            console.print("[red]❌ Incorrect[/red]")

        console.print(f"[bold]Feedback:[/bold] {result['feedback']}")

        if "hint" in result:
            console.print(f"[yellow]Hint:[/yellow] {result['hint']}")

    except Exception as e:
        console.print(f"[red]Error checking solution: {e}[/red]")


@app.command()
def demo():
    """Run a demo of the platform."""
    console.print("[bold blue]OpenGov-EarlyMathematics Demo[/bold blue]")
    console.print()

    # Demo curriculum
    console.print("[bold]1. Curriculum Overview:[/bold]")
    curriculum_manager = Curriculum()
    topics = curriculum_manager.get_topics_for_grade("3")
    console.print(f"Grade 3 topics: {[topic.value for topic in topics]}")
    console.print()

    # Demo problem generation
    console.print("[bold]2. Problem Generation:[/bold]")
    solver = MathProblemSolver()
    problem = solver.generate_problem("multiplication", 2, 3)
    console.print(f"Question: {problem.question}")
    console.print(f"Answer: {problem.answer}")
    console.print()

    # Demo solution checking
    console.print("[bold]3. Solution Checking:[/bold]")
    result = solver.check_solution("demo", "24")
    console.print(f"Feedback: {result['feedback']}")
    console.print()

    console.print("[green]Demo completed![/green]")


if __name__ == "__main__":  # pragma: no cover
    app()
