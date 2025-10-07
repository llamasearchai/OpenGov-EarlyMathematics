"""Terminal User Interface for OpenGov-EarlyMathematics."""


from rich.console import Console
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from opengov_earlymathematics.agents.math_agent import MathAgent
from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.learning_path import LearningPathGenerator
from opengov_earlymathematics.core.problem_engine import MathProblemSolver
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class MathEducationTUI(App):
    """Terminal User Interface for the mathematics education platform."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #header {
        dock: top;
        height: 3;
        background: blue;
    }

    #footer {
        dock: bottom;
        height: 1;
    }

    #main-content {
        layout: horizontal;
    }

    #sidebar {
        dock: left;
        width: 30;
        background: dark_blue;
    }

    #content-area {
        layout: vertical;
    }

    .lesson-card {
        margin: 1;
        padding: 1;
        background: white;
        border: solid $primary;
    }

    .problem-card {
        margin: 1;
        padding: 1;
        background: yellow;
    }
    """

    def __init__(self):
        super().__init__()
        self.curriculum = Curriculum()
        self.problem_solver = MathProblemSolver()
        self.learning_path_generator = LearningPathGenerator()
        self.math_agent = MathAgent()
        self.current_student_id = "demo_student"
        self.selected_topic = None

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header("OpenGov-EarlyMathematics - AI Math Education Platform")
        yield Footer()

        with Horizontal():
            # Sidebar
            with Vertical(id="sidebar"):
                yield Static("Menu", classes="sidebar-title")
                yield Button("Dashboard", id="btn-dashboard", variant="primary")
                yield Button("Learning Path", id="btn-learning-path", variant="default")
                yield Button("Practice Problems", id="btn-practice", variant="default")
                yield Button("AI Tutor", id="btn-tutor", variant="default")
                yield Button("Progress", id="btn-progress", variant="default")
                yield Button("Settings", id="btn-settings", variant="default")

            # Main content area
            with Vertical(id="content-area"):
                with TabbedContent():
                    with TabPane("Dashboard", id="tab-dashboard"):
                        yield self._create_dashboard_tab()

                    with TabPane("Learning Path", id="tab-learning-path"):
                        yield self._create_learning_path_tab()

                    with TabPane("Practice", id="tab-practice"):
                        yield self._create_practice_tab()

                    with TabPane("AI Tutor", id="tab-tutor"):
                        yield self._create_tutor_tab()

                    with TabPane("Progress", id="tab-progress"):
                        yield self._create_progress_tab()

                    with TabPane("Settings", id="tab-settings"):
                        yield self._create_settings_tab()

    def _create_dashboard_tab(self) -> ComposeResult:
        """Create dashboard tab content."""
        with Vertical():
            yield Static("Student Dashboard", classes="section-title")

            # Stats cards
            with Horizontal():
                yield Static("Current Streak: 7 days", classes="stat-card")
                yield Static("Problems Solved: 127", classes="stat-card")
                yield Static("Points: 2,450", classes="stat-card")
                yield Static("Mastery: 75%", classes="stat-card")

            yield Static("Today's Goals")
            goals = [
                "Complete multiplication lesson",
                "Solve 10 practice problems",
                "Review fraction concepts",
            ]
            for goal in goals:
                yield Static(f"[ ] {goal}")

    def _create_learning_path_tab(self) -> ComposeResult:
        """Create learning path tab content."""
        with Vertical():
            yield Static("My Learning Path", classes="section-title")

            # Current progress
            yield Static("Progress: 3 of 8 lessons completed")
            yield Static("[====================----------] 37%", classes="progress-bar")

            # Lessons list
            lessons = [
                ("[X] Introduction to Multiplication", "Multiplication", "30 min"),
                ("[ ] Multiplication Tables 6-10", "Multiplication", "25 min"),
                ("[ ] Introduction to Division", "Division", "35 min"),
                ("[ ] Fraction Basics", "Fractions", "40 min"),
            ]

            for lesson, topic, duration in lessons:
                with Horizontal(classes="lesson-card"):
                    yield Static(lesson)
                    yield Static(topic)
                    yield Static(duration)

    def _create_practice_tab(self) -> ComposeResult:
        """Create practice problems tab content."""
        with Vertical():
            yield Static("Practice Problems", classes="section-title")

            # Topic selection
            topics = ["Multiplication", "Division", "Fractions", "Addition", "Subtraction"]
            topic_select = Select(options=[(topic, topic) for topic in topics], id="topic-select")

            # Current problem
            yield Static("Current Problem:", classes="section-title")
            yield Static("What is 7 × 8?", classes="problem-card")

            # Answer input
            yield Input(placeholder="Enter your answer...", id="answer-input")

            # Action buttons
            with Horizontal():
                yield Button("Submit Answer", id="btn-submit", variant="primary")
                yield Button("Hint", id="btn-hint", variant="default")
                yield Button("Next Problem", id="btn-next", variant="default")

    def _create_tutor_tab(self) -> ComposeResult:
        """Create AI tutor tab content."""
        with Vertical():
            yield Static("AI Math Tutor", classes="section-title")
            yield Static(
                "Ask me anything about math! I'm here to help you understand concepts step by step."
            )

            # Chat area
            yield Static(
                "Tutor: Hi! I'm your AI math tutor. What would you like to learn about today?",
                id="chat-history",
            )

            # Question input
            yield Input(placeholder="Ask your math question...", id="tutor-input")

            # Quick topic buttons
            with Horizontal():
                yield Button("Multiplication", id="btn-mult", variant="default")
                yield Button("Fractions", id="btn-frac", variant="default")
                yield Button("Geometry", id="btn-geo", variant="default")

    def _create_progress_tab(self) -> ComposeResult:
        """Create progress tab content."""
        with Vertical():
            yield Static("My Progress", classes="section-title")

            # Topic mastery
            topics = {
                "Addition": 0.85,
                "Subtraction": 0.80,
                "Multiplication": 0.75,
                "Division": 0.60,
                "Fractions": 0.45,
            }

            for topic, mastery in topics.items():
                with Horizontal():
                    yield Static(f"{topic}:")
                    progress_chars = "=" * int(mastery * 20) + "-" * (20 - int(mastery * 20))
                    yield Static(f"[{progress_chars}] {mastery*100:.0f}%")

    def _create_settings_tab(self) -> ComposeResult:
        """Create settings tab content."""
        with Vertical():
            yield Static("Settings", classes="section-title")

            yield Label("Student ID:")
            yield Input(value=self.current_student_id, id="student-id-input")

            yield Label("Preferred Learning Style:")
            learning_styles = ["Visual", "Auditory", "Kinesthetic", "Reading/Writing"]
            yield Select(
                options=[(style, style) for style in learning_styles], id="learning-style-select"
            )

            yield Button("Save Settings", id="btn-save-settings", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id

        if button_id == "btn-dashboard":
            self.query_one(TabbedContent).active = "Dashboard"
        elif button_id == "btn-learning-path":
            self.query_one(TabbedContent).active = "Learning Path"
        elif button_id == "btn-practice":
            self.query_one(TabbedContent).active = "Practice"
        elif button_id == "btn-tutor":
            self.query_one(TabbedContent).active = "AI Tutor"
        elif button_id == "btn-progress":
            self.query_one(TabbedContent).active = "Progress"
        elif button_id == "btn-settings":
            self.query_one(TabbedContent).active = "Settings"
        elif button_id == "btn-submit":
            self._submit_answer()
        elif button_id == "btn-hint":
            self._show_hint()
        elif button_id == "btn-next":
            self._next_problem()
        elif button_id == "btn-save-settings":
            self._save_settings()
        elif button_id.startswith("btn-"):
            self._handle_quick_topic(button_id)

    def _submit_answer(self):
        """Submit answer to current problem."""
        answer_input = self.query_one("#answer-input", Input)
        answer = answer_input.value

        if answer == "56":
            self.notify("Correct! Great job!", title="Success")
        else:
            self.notify("Not quite right. Try again!", title="Keep Trying")

        answer_input.value = ""

    def _show_hint(self):
        """Show hint for current problem."""
        self.notify(
            "Think of 7 × 8 as 7 groups of 8, or (10 × 8) - (3 × 8) = 80 - 24 = 56", title="Hint"
        )

    def _next_problem(self):
        """Generate next problem."""
        self.notify("New problem generated!", title="Next Problem")

    def _save_settings(self):
        """Save user settings."""
        student_id_input = self.query_one("#student-id-input", Input)
        self.current_student_id = student_id_input.value
        self.notify(
            f"Settings saved for student: {self.current_student_id}", title="Settings Saved"
        )

    def _handle_quick_topic(self, button_id: str):
        """Handle quick topic selection."""
        topic_map = {
            "btn-mult": "Multiplication",
            "btn-frac": "Fractions",
            "btn-geo": "Geometry",
        }

        topic = topic_map.get(button_id)
        if topic:
            self.selected_topic = topic
            self.notify(f"Selected topic: {topic}", title="Topic Selected")


def run_tui():
    """Run the terminal user interface."""
    try:
        app = MathEducationTUI()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]Error running TUI: {e}[/red]")
        logger.error(f"TUI error: {e}")


if __name__ == "__main__":
    run_tui()
