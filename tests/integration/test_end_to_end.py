"""End-to-end integration tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.learning_path import LearningPathGenerator
from opengov_earlymathematics.core.models import GradeLevel, MathTopic
from opengov_earlymathematics.core.problem_engine import MathProblemSolver


class TestEndToEnd:
    """Test complete user workflows."""

    def test_complete_student_journey(self):
        """Test complete student learning journey."""
        # Step 1: Get curriculum for grade
        curriculum = Curriculum()
        topics = curriculum.get_topics_for_grade(GradeLevel.GRADE_3)
        assert len(topics) > 0

        # Step 2: Generate practice problems
        solver = MathProblemSolver()
        problem = solver.generate_problem("multiplication", 1, 3)
        assert problem.topic == MathTopic.MULTIPLICATION

        # Step 3: Check solution
        result = solver.check_solution(problem.id, problem.answer)
        assert result["correct"] is True

        # Step 4: Create learning path
        generator = LearningPathGenerator()
        assessment = {"multiplication": 0.75, "division": 0.60}
        path = generator.create_path(
            student_id="test_student",
            grade_level=3,
            assessment_results=assessment,
        )
        assert len(path.lessons) > 0

    def test_lesson_with_problems(self):
        """Test retrieving lesson with practice problems."""
        curriculum = Curriculum()
        lesson = curriculum.get_lesson("lesson_mult_3_1")
        assert lesson is not None
        assert len(lesson.practice_problems) > 0

        # Get first practice problem for lesson
        problem_id = lesson.practice_problems[0]
        problem = curriculum.get_problem(problem_id)
        assert problem is not None

    def test_topic_progression(self):
        """Test progression through topic."""
        solver = MathProblemSolver()

        # Generate problems at different difficulty levels
        beginner = solver.generate_problem("multiplication", 1, 3)
        intermediate = solver.generate_problem("multiplication", 2, 3)
        advanced = solver.generate_problem("multiplication", 3, 3)

        assert beginner.difficulty.value == "beginner"
        assert intermediate.difficulty.value == "intermediate"
        assert advanced.difficulty.value == "advanced"

    def test_practice_set_workflow(self):
        """Test generating and working through practice set."""
        solver = MathProblemSolver()
        problems = solver.generate_practice_set(MathTopic.BASIC_ADDITION, num_problems=5)

        assert len(problems) == 5

        # Work through problems
        correct_count = 0
        for problem in problems:
            result = solver.check_solution(problem.id, problem.answer)
            if result["correct"]:
                correct_count += 1

        assert correct_count == 5  # All should be correct with actual answers
