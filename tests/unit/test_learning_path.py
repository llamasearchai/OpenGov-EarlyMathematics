"""Unit tests for learning path generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from opengov_earlymathematics.core.learning_path import LearningPathGenerator
from opengov_earlymathematics.core.models import MathTopic


class TestLearningPathGenerator:
    """Test LearningPathGenerator class."""

    def test_init(self):
        """Test generator initialization."""
        generator = LearningPathGenerator()
        assert generator.curriculum is not None
        assert generator.student_model is not None

    def test_create_path_basic(self):
        """Test creating basic learning path."""
        generator = LearningPathGenerator()
        assessment = {
            "multiplication": 0.75,
            "division": 0.60,
            "fractions": 0.40,
        }

        path = generator.create_path(
            student_id="student_1",
            grade_level=3,
            assessment_results=assessment,
        )

        assert path.student_id == "student_1"
        assert len(path.lessons) > 0
        assert len(path.recommended_topics) > 0
        assert path.estimated_completion_date is not None

    def test_create_path_with_goals(self):
        """Test creating path with learning goals."""
        generator = LearningPathGenerator()
        assessment = {"multiplication": 0.80}
        goals = ["Master multiplication tables", "Learn division"]

        path = generator.create_path(
            student_id="student_2",
            grade_level=3,
            assessment_results=assessment,
            goals=goals,
        )

        assert path.learning_goals == goals
        assert len(path.learning_goals) == 2

    def test_create_path_with_learning_style(self):
        """Test creating path with specific learning style."""
        generator = LearningPathGenerator()
        assessment = {"basic_addition": 0.70}

        path = generator.create_path(
            student_id="student_3",
            grade_level=2,
            assessment_results=assessment,
            learning_style="visual",  # Use valid learning style
        )

        assert path.student_id == "student_3"
        # Path is created even if no lessons available
        assert path.id is not None

    def test_mastery_scores_populated(self):
        """Test that mastery scores are populated."""
        generator = LearningPathGenerator()
        assessment = {
            "multiplication": 0.85,
            "division": 0.70,
        }

        path = generator.create_path(
            student_id="student_4",
            grade_level=3,
            assessment_results=assessment,
        )

        assert len(path.mastery_scores) > 0

    def test_path_id_unique(self):
        """Test that path IDs are unique."""
        generator = LearningPathGenerator()
        assessment = {"multiplication": 0.75}

        path1 = generator.create_path("student_5", 3, assessment)
        path2 = generator.create_path("student_5", 3, assessment)

        assert path1.id != path2.id

    def test_different_grade_levels(self):
        """Test creating paths for different grade levels."""
        generator = LearningPathGenerator()
        assessment_1 = {"counting": 0.60}
        assessment_5 = {"fractions": 0.70}

        path_1 = generator.create_path("student_6", 1, assessment_1)
        path_5 = generator.create_path("student_7", 5, assessment_5)

        assert path_1.student_id == "student_6"
        assert path_5.student_id == "student_7"
