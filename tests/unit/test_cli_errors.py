"""Tests to cover CLI exception branches."""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from typer.testing import CliRunner

from opengov_earlymathematics.cli import app


runner = CliRunner()


def test_cli_generate_problem_error():
    with patch(
        "opengov_earlymathematics.core.problem_engine.MathProblemSolver.generate_problem",
        side_effect=Exception("oops"),
    ):
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
    assert "Error generating problem" in result.stdout


def test_cli_check_solution_error():
    with patch(
        "opengov_earlymathematics.core.problem_engine.MathProblemSolver.check_solution",
        side_effect=Exception("oops"),
    ):
        result = runner.invoke(
            app,
            ["check-solution", "--problem-id", "pid", "--answer", "42"],
        )
    assert result.exit_code == 0
    assert "Error checking solution" in result.stdout


def test_cli_check_solution_incorrect_and_hint():
    result = runner.invoke(
        app,
        ["check-solution", "--problem-id", "pid", "--answer", "not-a-number"],
    )
    assert result.exit_code == 0
    assert "Incorrect" in result.stdout
    assert "Hint" in result.stdout


def test_curriculum_all_grades_with_value_error_in_loop():
    # Patch GradeLevel to raise for any value to exercise continue path
    with patch(
        "opengov_earlymathematics.core.models.GradeLevel", side_effect=ValueError("bad")
    ):
        result = runner.invoke(app, ["curriculum"])  # no grade filter -> loop over defaults
    assert result.exit_code == 0
    # Still prints table header despite errors
    assert "Curriculum" in result.stdout or "Grade" in result.stdout
