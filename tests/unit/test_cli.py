"""Unit tests for CLI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from opengov_earlymathematics.cli import app

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_version(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "OpenGov-EarlyMathematics" in result.stdout
        assert "0.1.0" in result.stdout

    def test_curriculum_all_grades(self):
        """Test curriculum command without grade filter."""
        result = runner.invoke(app, ["curriculum"])
        assert result.exit_code == 0
        assert "Curriculum" in result.stdout

    def test_curriculum_specific_grade(self):
        """Test curriculum command with grade filter."""
        result = runner.invoke(app, ["curriculum", "--grade", "3"])
        assert result.exit_code == 0
        assert "Grade 3" in result.stdout or "multiplication" in result.stdout

    def test_curriculum_invalid_grade(self):
        """Test curriculum command with invalid grade."""
        result = runner.invoke(app, ["curriculum", "--grade", "invalid"])
        assert result.exit_code == 0
        assert "Invalid" in result.stdout

    def test_generate_problem(self):
        """Test generate-problem command."""
        result = runner.invoke(
            app,
            [
                "generate-problem",
                "--topic",
                "multiplication",
                "--difficulty",
                "2",
                "--grade",
                "3",
            ],
        )
        assert result.exit_code == 0
        assert "Generated Problem" in result.stdout or "Question" in result.stdout

    def test_check_solution(self):
        """Test check-solution command."""
        result = runner.invoke(
            app,
            ["check-solution", "--problem-id", "test_1", "--answer", "42"],
        )
        assert result.exit_code == 0
        assert "Feedback" in result.stdout

    def test_demo(self):
        """Test demo command."""
        result = runner.invoke(app, ["demo"])
        assert result.exit_code == 0
        assert "Demo" in result.stdout
        assert "completed" in result.stdout

    def test_demo_shows_curriculum(self):
        """Test demo shows curriculum overview."""
        result = runner.invoke(app, ["demo"])
        assert "Curriculum" in result.stdout or "Grade" in result.stdout

    def test_demo_shows_problem(self):
        """Test demo shows problem generation."""
        result = runner.invoke(app, ["demo"])
        assert "Problem" in result.stdout or "Question" in result.stdout

    def test_demo_shows_solution(self):
        """Test demo shows solution checking."""
        result = runner.invoke(app, ["demo"])
        assert "Solution" in result.stdout or "Feedback" in result.stdout
