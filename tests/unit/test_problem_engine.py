"""Unit tests for problem engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.core.models import DifficultyLevel, MathTopic
from opengov_earlymathematics.core.problem_engine import MathProblemSolver


class TestMathProblemSolver:
    """Test MathProblemSolver class."""

    def test_init(self):
        """Test solver initialization."""
        solver = MathProblemSolver()
        assert solver.generators is not None
        assert len(solver.generators) > 0

    def test_generate_addition_problem(self):
        """Test generating addition problem."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("basic_addition", 1, 3)
        assert problem.topic == MathTopic.BASIC_ADDITION
        assert problem.difficulty == DifficultyLevel.BEGINNER
        assert "+" in problem.question
        assert problem.answer is not None

    def test_generate_subtraction_problem(self):
        """Test generating subtraction problem."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("basic_subtraction", 2, 4)
        assert problem.topic == MathTopic.BASIC_SUBTRACTION
        assert "-" in problem.question
        assert len(problem.solution_steps) > 0

    def test_generate_multiplication_problem(self):
        """Test generating multiplication problem."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("multiplication", 1, 3)
        assert problem.topic == MathTopic.MULTIPLICATION
        assert "×" in problem.question
        assert len(problem.hints) > 0

    def test_generate_division_problem(self):
        """Test generating division problem."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("division", 1, 4)
        assert problem.topic == MathTopic.DIVISION
        assert "÷" in problem.question

    def test_generate_fractions_problem(self):
        """Test generating fractions problem."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("fractions", 1, 5)
        assert problem.topic == MathTopic.FRACTIONS
        assert "/" in problem.question or "/" in problem.answer

    def test_generate_algebra_problem(self):
        """Test generating algebra problem."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("algebra_1", 1, 8)
        assert problem.topic == MathTopic.ALGEBRA_1
        assert "x" in problem.question

    def test_generate_problem_different_difficulties(self):
        """Test generating problems with different difficulties."""
        solver = MathProblemSolver()

        beginner = solver.generate_problem("multiplication", 1, 3)
        expert = solver.generate_problem("multiplication", 4, 3)

        assert beginner.difficulty == DifficultyLevel.BEGINNER
        assert expert.difficulty == DifficultyLevel.EXPERT

    def test_check_solution_correct(self):
        """Test checking correct solution."""
        solver = MathProblemSolver()
        result = solver.check_solution("prob_1", "42")
        assert result["correct"] is True
        assert "correct" in result["feedback"].lower()

    def test_check_solution_incorrect(self):
        """Test checking incorrect solution."""
        solver = MathProblemSolver()
        result = solver.check_solution("prob_1", "invalid")
        assert result["correct"] is False

    def test_check_solution_with_steps(self):
        """Test checking solution with steps."""
        solver = MathProblemSolver()
        result = solver.check_solution("prob_1", "42", show_steps=True)
        assert "feedback" in result

    def test_check_solution_fraction(self):
        """Test checking fraction answer."""
        solver = MathProblemSolver()
        result = solver.check_solution("prob_1", "3/4")
        assert result["correct"] is True

    def test_check_solution_negative(self):
        """Test checking negative number answer."""
        solver = MathProblemSolver()
        result = solver.check_solution("prob_1", "-5")
        assert result["correct"] is True

    def test_generate_practice_set(self):
        """Test generating practice set."""
        solver = MathProblemSolver()
        problems = solver.generate_practice_set(
            MathTopic.MULTIPLICATION, num_problems=5
        )
        assert len(problems) == 5
        assert all(p.topic == MathTopic.MULTIPLICATION for p in problems)

    def test_generate_practice_set_with_difficulty(self):
        """Test generating practice set with difficulty."""
        solver = MathProblemSolver()
        problems = solver.generate_practice_set(
            MathTopic.BASIC_ADDITION,
            num_problems=3,
            difficulty=DifficultyLevel.ADVANCED,
        )
        assert len(problems) == 3
        assert all(p.difficulty == DifficultyLevel.ADVANCED for p in problems)

    def test_addition_beginner_range(self):
        """Test addition beginner uses appropriate number range."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("basic_addition", 1, 1)
        # Check that answer is reasonable for beginner level
        answer = int(problem.answer)
        assert 2 <= answer <= 20

    def test_addition_expert_range(self):
        """Test addition expert uses larger numbers."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("basic_addition", 4, 5)
        # Check that answer is larger for expert level
        answer = int(problem.answer)
        assert answer >= 200

    def test_subtraction_positive_result(self):
        """Test subtraction always gives positive result."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("basic_subtraction", 1, 2)
        answer = int(problem.answer)
        assert answer >= 0

    def test_division_even(self):
        """Test division problems have integer answers."""
        solver = MathProblemSolver()
        for _ in range(5):
            problem = solver.generate_problem("division", 1, 3)
            answer = problem.answer
            assert "/" not in answer  # Should be whole number

    def test_problem_has_required_fields(self):
        """Test that generated problems have all required fields."""
        solver = MathProblemSolver()
        problem = solver.generate_problem("multiplication", 2, 3)
        assert problem.question
        assert problem.answer
        assert len(problem.solution_steps) > 0
        assert len(problem.hints) > 0
        assert problem.explanation
