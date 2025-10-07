"""Unit tests for curriculum management."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.models import GradeLevel, MathTopic


class TestCurriculum:
    """Test Curriculum class."""

    def test_init(self):
        """Test curriculum initialization."""
        curriculum = Curriculum()
        assert curriculum.topics_by_grade is not None
        assert curriculum.lessons is not None
        assert curriculum.problems is not None

    def test_get_topics_for_grade_k(self):
        """Test getting topics for kindergarten."""
        curriculum = Curriculum()
        topics = curriculum.get_topics_for_grade(GradeLevel.KINDERGARTEN)
        assert len(topics) > 0
        assert MathTopic.COUNTING in topics
        assert MathTopic.SHAPES in topics

    def test_get_topics_for_grade_3(self):
        """Test getting topics for grade 3."""
        curriculum = Curriculum()
        topics = curriculum.get_topics_for_grade(GradeLevel.GRADE_3)
        assert len(topics) > 0
        assert MathTopic.MULTIPLICATION in topics
        assert MathTopic.DIVISION in topics

    def test_get_topics_for_grade_12(self):
        """Test getting topics for grade 12."""
        curriculum = Curriculum()
        topics = curriculum.get_topics_for_grade(GradeLevel.GRADE_12)
        assert len(topics) > 0
        assert MathTopic.CALCULUS in topics

    def test_get_lesson(self):
        """Test getting a specific lesson."""
        curriculum = Curriculum()
        lesson = curriculum.get_lesson("lesson_mult_3_1")
        assert lesson is not None
        assert lesson.title == "Introduction to Multiplication"
        assert lesson.topic == MathTopic.MULTIPLICATION

    def test_get_lesson_nonexistent(self):
        """Test getting a non-existent lesson."""
        curriculum = Curriculum()
        lesson = curriculum.get_lesson("nonexistent")
        assert lesson is None

    def test_get_problem(self):
        """Test getting a specific problem."""
        curriculum = Curriculum()
        problem = curriculum.get_problem("prob_mult_1")
        assert problem is not None
        assert problem.question == "What is 3 × 4?"
        assert problem.answer == "12"

    def test_get_problem_nonexistent(self):
        """Test getting a non-existent problem."""
        curriculum = Curriculum()
        problem = curriculum.get_problem("nonexistent")
        assert problem is None

    def test_get_lessons_for_topic(self):
        """Test getting lessons for a topic."""
        curriculum = Curriculum()
        lessons = curriculum.get_lessons_for_topic(MathTopic.MULTIPLICATION)
        assert len(lessons) > 0
        assert all(lesson.topic == MathTopic.MULTIPLICATION for lesson in lessons)

    def test_get_lessons_for_topic_with_grade(self):
        """Test getting lessons for a topic and grade."""
        curriculum = Curriculum()
        lessons = curriculum.get_lessons_for_topic(
            MathTopic.MULTIPLICATION, GradeLevel.GRADE_3
        )
        assert len(lessons) > 0
        assert all(lesson.grade_level == GradeLevel.GRADE_3 for lesson in lessons)

    def test_get_problems_for_topic(self):
        """Test getting problems for a topic."""
        curriculum = Curriculum()
        problems = curriculum.get_problems_for_topic(MathTopic.MULTIPLICATION)
        assert len(problems) > 0
        assert all(problem.topic == MathTopic.MULTIPLICATION for problem in problems)

    def test_get_problems_for_topic_with_difficulty(self):
        """Test getting problems for a topic with difficulty filter."""
        curriculum = Curriculum()
        problems = curriculum.get_problems_for_topic(
            MathTopic.MULTIPLICATION, difficulty="beginner"
        )
        assert len(problems) > 0
        assert all(problem.difficulty == "beginner" for problem in problems)

    def test_sample_content_exists(self):
        """Test that sample content is created."""
        curriculum = Curriculum()
        assert "lesson_mult_3_1" in curriculum.lessons
        assert "prob_mult_1" in curriculum.problems

    def test_lesson_structure(self):
        """Test lesson structure is correct."""
        curriculum = Curriculum()
        lesson = curriculum.get_lesson("lesson_mult_3_1")
        assert len(lesson.objectives) > 0
        assert len(lesson.content_blocks) > 0
        assert len(lesson.practice_problems) > 0

    def test_problem_structure(self):
        """Test problem structure is correct."""
        curriculum = Curriculum()
        problem = curriculum.get_problem("prob_mult_1")
        assert len(problem.solution_steps) > 0
        assert len(problem.hints) > 0
        assert problem.explanation != ""
