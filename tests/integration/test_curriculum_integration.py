"""Integration tests for curriculum system."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.models import GradeLevel, MathTopic


class TestCurriculumIntegration:
    """Test curriculum integration."""

    def test_all_grades_have_topics(self):
        """Test that all grade levels have assigned topics."""
        curriculum = Curriculum()

        for grade in [
            GradeLevel.KINDERGARTEN,
            GradeLevel.GRADE_1,
            GradeLevel.GRADE_3,
            GradeLevel.GRADE_5,
            GradeLevel.GRADE_8,
            GradeLevel.GRADE_12,
        ]:
            topics = curriculum.get_topics_for_grade(grade)
            assert len(topics) > 0, f"Grade {grade} should have topics"

    def test_topic_availability_across_grades(self):
        """Test that topics are available across appropriate grades."""
        curriculum = Curriculum()

        # Multiplication should be in elementary grades
        mult_grades = []
        for grade in [
            GradeLevel.GRADE_3,
            GradeLevel.GRADE_4,
            GradeLevel.GRADE_5,
        ]:
            topics = curriculum.get_topics_for_grade(grade)
            if MathTopic.MULTIPLICATION in topics:
                mult_grades.append(grade)

        assert len(mult_grades) > 0, "Multiplication should be in multiple grades"

    def test_progression_difficulty(self):
        """Test that topics progress in difficulty."""
        curriculum = Curriculum()

        # Early grades should have basic topics
        k_topics = curriculum.get_topics_for_grade(GradeLevel.KINDERGARTEN)
        assert MathTopic.COUNTING in k_topics
        assert MathTopic.CALCULUS not in k_topics

        # High school should have advanced topics
        grade_12_topics = curriculum.get_topics_for_grade(GradeLevel.GRADE_12)
        assert MathTopic.CALCULUS in grade_12_topics
        assert MathTopic.COUNTING not in grade_12_topics

    def test_lesson_problem_consistency(self):
        """Test that lessons reference problems."""
        curriculum = Curriculum()

        # Check that sample lesson exists
        lesson = curriculum.get_lesson("lesson_mult_3_1")
        assert lesson is not None
        assert len(lesson.practice_problems) > 0

        # Check that sample problem exists
        problem = curriculum.get_problem("prob_mult_1")
        assert problem is not None
        assert problem.topic is not None
