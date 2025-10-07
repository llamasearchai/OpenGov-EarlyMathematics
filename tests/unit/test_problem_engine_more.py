"""Additional tests for MathProblemSolver branches and validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from opengov_earlymathematics.core.problem_engine import MathProblemSolver


def test_generate_problem_default_generator_for_unmapped_topic():
    solver = MathProblemSolver()
    # geometry is a valid topic but not explicitly mapped -> uses default generator
    problem = solver.generate_problem("geometry", difficulty_level=2, student_level=3)
    assert problem.question
    assert problem.answer


def test_generate_problem_fraction_and_algebra_advanced():
    solver = MathProblemSolver()

    p_frac = solver.generate_problem("fractions", difficulty_level=3, student_level=5)
    assert "/" in p_frac.answer or p_frac.answer.isdigit()

    p_alg = solver.generate_problem("algebra_1", difficulty_level=2, student_level=8)
    assert "x" in " ".join(p_alg.solution_steps)


def test_check_solution_with_steps_for_invalid_answer():
    solver = MathProblemSolver()
    result = solver.check_solution("pid", student_answer="not-a-number", show_steps=True)
    assert not result["correct"]
    assert "hint" in result and "next_step" in result


def test_subtraction_and_division_difficulty_branches():
    solver = MathProblemSolver()
    # Advanced subtraction path triggers the else branch
    p_sub = solver.generate_problem("basic_subtraction", difficulty_level=4, student_level=3)
    assert "-" in p_sub.question

    # Division intermediate and advanced branches
    p_div_mid = solver.generate_problem("division", difficulty_level=2, student_level=4)
    assert "÷" in p_div_mid.question
    p_div_adv = solver.generate_problem("division", difficulty_level=3, student_level=5)
    assert "÷" in p_div_adv.question
