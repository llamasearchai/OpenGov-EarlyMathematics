"""Unit tests for core models."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from datetime import datetime

import pytest

from opengov_earlymathematics.core.models import (
    Assessment,
    DifficultyLevel,
    GradeLevel,
    LearningPath,
    LearningStyle,
    Lesson,
    MathTopic,
    Problem,
    Progress,
    Session,
    Student,
    Teacher,
)


class TestEnums:
    """Test enum models."""

    def test_grade_level(self):
        """Test grade level enum."""
        assert GradeLevel.KINDERGARTEN == "K"
        assert GradeLevel.GRADE_1 == "1"
        assert GradeLevel.GRADE_12 == "12"

    def test_difficulty_level(self):
        """Test difficulty level enum."""
        assert DifficultyLevel.BEGINNER == "beginner"
        assert DifficultyLevel.EXPERT == "expert"

    def test_learning_style(self):
        """Test learning style enum."""
        assert LearningStyle.VISUAL == "visual"
        assert LearningStyle.KINESTHETIC == "kinesthetic"

    def test_math_topic(self):
        """Test math topic enum."""
        assert MathTopic.COUNTING == "counting"
        assert MathTopic.CALCULUS == "calculus"


class TestStudent:
    """Test Student model."""

    def test_create_student(self):
        """Test creating a student."""
        student = Student(
            id="student_1",
            name="Test Student",
            grade_level=GradeLevel.GRADE_3,
            age=8,
        )
        assert student.id == "student_1"
        assert student.name == "Test Student"
        assert student.grade_level == GradeLevel.GRADE_3
        assert student.age == 8
        assert student.points == 0
        assert student.current_streak == 0

    def test_student_with_optional_fields(self):
        """Test student with optional fields."""
        student = Student(
            id="student_2",
            name="Advanced Student",
            email="student@example.com",
            grade_level=GradeLevel.GRADE_5,
            age=10,
            parent_email="parent@example.com",
            points=150,
            current_streak=5,
        )
        assert student.email == "student@example.com"
        assert student.parent_email == "parent@example.com"
        assert student.points == 150
        assert student.current_streak == 5


class TestProblem:
    """Test Problem model."""

    def test_create_problem(self):
        """Test creating a problem."""
        problem = Problem(
            id="prob_1",
            topic=MathTopic.MULTIPLICATION,
            grade_level=GradeLevel.GRADE_3,
            difficulty=DifficultyLevel.BEGINNER,
            question="What is 2 × 3?",
            answer="6",
            solution_steps=["2 × 3 = 6"],
            explanation="Multiplication problem",
        )
        assert problem.id == "prob_1"
        assert problem.topic == MathTopic.MULTIPLICATION
        assert problem.question == "What is 2 × 3?"
        assert problem.answer == "6"

    def test_problem_with_hints(self):
        """Test problem with hints."""
        problem = Problem(
            id="prob_2",
            topic=MathTopic.DIVISION,
            grade_level=GradeLevel.GRADE_4,
            difficulty=DifficultyLevel.INTERMEDIATE,
            question="What is 12 ÷ 3?",
            answer="4",
            solution_steps=["12 ÷ 3 = 4"],
            hints=["Think of groups", "How many 3s in 12?"],
            explanation="Division problem",
        )
        assert len(problem.hints) == 2
        assert problem.hints[0] == "Think of groups"


class TestLesson:
    """Test Lesson model."""

    def test_create_lesson(self):
        """Test creating a lesson."""
        lesson = Lesson(
            id="lesson_1",
            title="Introduction to Multiplication",
            topic=MathTopic.MULTIPLICATION,
            grade_level=GradeLevel.GRADE_3,
            duration_minutes=30,
            objectives=["Understand multiplication"],
            content_blocks=[{"type": "intro", "content": "test"}],
            practice_problems=["prob_1"],
        )
        assert lesson.id == "lesson_1"
        assert lesson.title == "Introduction to Multiplication"
        assert lesson.duration_minutes == 30
        assert len(lesson.objectives) == 1


class TestSession:
    """Test Session model."""

    def test_create_session(self):
        """Test creating a session."""
        session = Session(
            id="session_1",
            student_id="student_1",
        )
        assert session.id == "session_1"
        assert session.student_id == "student_1"
        assert session.problems_attempted == 0
        assert session.problems_correct == 0

    def test_session_with_metrics(self):
        """Test session with performance metrics."""
        session = Session(
            id="session_2",
            student_id="student_2",
            problems_attempted=10,
            problems_correct=8,
            hints_used=2,
            points_earned=80,
        )
        assert session.problems_attempted == 10
        assert session.problems_correct == 8
        assert session.hints_used == 2
        assert session.points_earned == 80


class TestProgress:
    """Test Progress model."""

    def test_create_progress(self):
        """Test creating progress tracker."""
        progress = Progress(
            student_id="student_1",
        )
        assert progress.student_id == "student_1"
        assert progress.current_grade_progress == 0.0
        assert progress.engagement_score == 0.5

    def test_progress_with_mastery(self):
        """Test progress with topic mastery."""
        progress = Progress(
            student_id="student_2",
            topic_mastery={MathTopic.MULTIPLICATION: 0.85, MathTopic.DIVISION: 0.70},
            current_grade_progress=0.75,
        )
        assert progress.topic_mastery[MathTopic.MULTIPLICATION] == 0.85
        assert progress.current_grade_progress == 0.75


class TestTeacher:
    """Test Teacher model."""

    def test_create_teacher(self):
        """Test creating a teacher."""
        teacher = Teacher(
            id="teacher_1",
            name="Mr. Smith",
            email="smith@example.com",
            subjects=[MathTopic.MULTIPLICATION, MathTopic.DIVISION],
            grade_levels=[GradeLevel.GRADE_3, GradeLevel.GRADE_4],
            experience_years=10,
        )
        assert teacher.name == "Mr. Smith"
        assert teacher.experience_years == 10
        assert len(teacher.subjects) == 2


class TestAssessment:
    """Test Assessment model."""

    def test_create_assessment(self):
        """Test creating an assessment."""
        assessment = Assessment(
            id="assessment_1",
            title="Multiplication Quiz",
            type="quiz",
            grade_level=GradeLevel.GRADE_3,
            topics=[MathTopic.MULTIPLICATION],
            problems=["prob_1", "prob_2"],
        )
        assert assessment.title == "Multiplication Quiz"
        assert assessment.type == "quiz"
        assert assessment.passing_score == 0.7
        assert assessment.allow_retries is True


class TestLearningPath:
    """Test LearningPath model."""

    def test_create_learning_path(self):
        """Test creating a learning path."""
        path = LearningPath(
            id="path_1",
            student_id="student_1",
            lessons=["lesson_1", "lesson_2"],
        )
        assert path.student_id == "student_1"
        assert path.current_lesson == 0
        assert len(path.lessons) == 2
