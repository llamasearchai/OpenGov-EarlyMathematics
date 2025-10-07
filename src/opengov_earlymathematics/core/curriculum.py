"""Curriculum management and content organization."""

from typing import Dict, List, Optional

from opengov_earlymathematics.core.models import (
    GradeLevel,
    Lesson,
    MathTopic,
    Problem,
)
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class Curriculum:
    """Manages the mathematics curriculum."""

    def __init__(self):
        """Initialize curriculum."""
        self.topics_by_grade = self._initialize_curriculum()
        self.lessons: Dict[str, Lesson] = {}
        self.problems: Dict[str, Problem] = {}
        self._load_content()

    def _initialize_curriculum(self) -> Dict[GradeLevel, List[MathTopic]]:
        """Initialize curriculum structure by grade."""
        return {
            GradeLevel.KINDERGARTEN: [
                MathTopic.COUNTING,
                MathTopic.NUMBER_RECOGNITION,
                MathTopic.SHAPES,
                MathTopic.PATTERNS,
            ],
            GradeLevel.GRADE_1: [
                MathTopic.COUNTING,
                MathTopic.BASIC_ADDITION,
                MathTopic.BASIC_SUBTRACTION,
                MathTopic.SHAPES,
                MathTopic.MEASUREMENT,
            ],
            GradeLevel.GRADE_2: [
                MathTopic.BASIC_ADDITION,
                MathTopic.BASIC_SUBTRACTION,
                MathTopic.TIME,
                MathTopic.MONEY,
                MathTopic.MEASUREMENT,
            ],
            GradeLevel.GRADE_3: [
                MathTopic.MULTIPLICATION,
                MathTopic.DIVISION,
                MathTopic.FRACTIONS,
                MathTopic.GEOMETRY,
                MathTopic.WORD_PROBLEMS,
            ],
            GradeLevel.GRADE_4: [
                MathTopic.MULTIPLICATION,
                MathTopic.DIVISION,
                MathTopic.FRACTIONS,
                MathTopic.DECIMALS,
                MathTopic.DATA_GRAPHS,
            ],
            GradeLevel.GRADE_5: [
                MathTopic.FRACTIONS,
                MathTopic.DECIMALS,
                MathTopic.GEOMETRY,
                MathTopic.DATA_GRAPHS,
                MathTopic.WORD_PROBLEMS,
            ],
            GradeLevel.GRADE_6: [
                MathTopic.PRE_ALGEBRA,
                MathTopic.RATIOS,
                MathTopic.PROPORTIONS,
                MathTopic.STATISTICS,
                MathTopic.COORDINATE_GEOMETRY,
            ],
            GradeLevel.GRADE_7: [
                MathTopic.PRE_ALGEBRA,
                MathTopic.PROPORTIONS,
                MathTopic.STATISTICS,
                MathTopic.PROBABILITY,
                MathTopic.ALGEBRAIC_THINKING,
            ],
            GradeLevel.GRADE_8: [
                MathTopic.ALGEBRA_1,
                MathTopic.COORDINATE_GEOMETRY,
                MathTopic.STATISTICS,
                MathTopic.PROBABILITY,
                MathTopic.ALGEBRAIC_THINKING,
            ],
            GradeLevel.GRADE_9: [
                MathTopic.ALGEBRA_1,
                MathTopic.GEOMETRY_ADVANCED,
            ],
            GradeLevel.GRADE_10: [
                MathTopic.ALGEBRA_2,
                MathTopic.GEOMETRY_ADVANCED,
            ],
            GradeLevel.GRADE_11: [
                MathTopic.ALGEBRA_2,
                MathTopic.TRIGONOMETRY,
                MathTopic.PRE_CALCULUS,
            ],
            GradeLevel.GRADE_12: [
                MathTopic.PRE_CALCULUS,
                MathTopic.CALCULUS,
                MathTopic.STATISTICS,
            ],
        }

    def _load_content(self):
        """Load curriculum content from files."""
        # Load pre-built lessons and problems
        # In production, this would load from a database or content repository
        self._create_sample_content()

    def _create_sample_content(self):
        """Create sample curriculum content."""
        # Sample lesson for Grade 3 Multiplication
        self.lessons["lesson_mult_3_1"] = Lesson(
            id="lesson_mult_3_1",
            title="Introduction to Multiplication",
            topic=MathTopic.MULTIPLICATION,
            grade_level=GradeLevel.GRADE_3,
            duration_minutes=30,
            objectives=[
                "Understand multiplication as repeated addition",
                "Learn multiplication tables 1-5",
                "Solve simple multiplication problems",
            ],
            content_blocks=[
                {
                    "type": "introduction",
                    "content": "Multiplication is a fast way of adding the same number many times!",
                    "visual": "multiplication_intro.png",
                },
                {
                    "type": "example",
                    "content": "3 × 4 means adding 3 four times: 3 + 3 + 3 + 3 = 12",
                    "interactive": True,
                },
                {
                    "type": "practice",
                    "problems": ["prob_mult_1", "prob_mult_2", "prob_mult_3"],
                },
            ],
            practice_problems=["prob_mult_1", "prob_mult_2", "prob_mult_3"],
            resources=["multiplication_table.pdf", "visual_arrays.png"],
            interactive_elements=[
                {"type": "manipulative", "id": "array_builder"},
                {"type": "game", "id": "multiplication_race"},
            ],
        )

        # Sample problem
        self.problems["prob_mult_1"] = Problem(
            id="prob_mult_1",
            topic=MathTopic.MULTIPLICATION,
            grade_level=GradeLevel.GRADE_3,
            difficulty="beginner",
            question="What is 3 × 4?",
            answer="12",
            solution_steps=[
                "Think of 3 × 4 as 3 groups of 4",
                "Count: 4 + 4 + 4",
                "4 + 4 = 8",
                "8 + 4 = 12",
                "So, 3 × 4 = 12",
            ],
            hints=[
                "Try drawing 3 groups with 4 items in each group",
                "Count all the items you drew",
                "You can also add 4 three times: 4 + 4 + 4",
            ],
            visual_aids=["multiplication_visual_3x4.png"],
            explanation="Multiplication is repeated addition. When we multiply 3 × 4, we add 3 groups of 4 together.",
        )

    def get_topics_for_grade(self, grade: GradeLevel) -> List[MathTopic]:
        """Get topics for a specific grade level."""
        return self.topics_by_grade.get(grade, [])

    def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get a specific lesson."""
        return self.lessons.get(lesson_id)

    def get_problem(self, problem_id: str) -> Optional[Problem]:
        """Get a specific problem."""
        return self.problems.get(problem_id)

    def get_lessons_for_topic(
        self,
        topic: MathTopic,
        grade: Optional[GradeLevel] = None,
    ) -> List[Lesson]:
        """Get all lessons for a topic."""
        lessons = []
        for lesson in self.lessons.values():
            if lesson.topic == topic:
                if grade is None or lesson.grade_level == grade:
                    lessons.append(lesson)
        return lessons

    def get_problems_for_topic(
        self,
        topic: MathTopic,
        difficulty: Optional[str] = None,
    ) -> List[Problem]:
        """Get problems for a topic."""
        problems = []
        for problem in self.problems.values():
            if problem.topic == topic:
                if difficulty is None or problem.difficulty == difficulty:
                    problems.append(problem)
        return problems
