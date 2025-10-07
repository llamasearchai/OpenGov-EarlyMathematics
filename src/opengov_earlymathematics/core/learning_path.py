"""Personalized learning path generation."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from opengov_earlymathematics.config import settings
from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.models import (
    DifficultyLevel,
    GradeLevel,
    LearningPath,
    LearningStyle,
    MathTopic,
    Student,
)
from opengov_earlymathematics.ml.student_model import StudentModel
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class LearningPathGenerator:
    """Generates and manages personalized learning paths."""

    def __init__(self):
        """Initialize learning path generator."""
        self.curriculum = Curriculum()
        self.student_model = StudentModel()

    def create_path(
        self,
        student_id: str,
        grade_level: int,
        assessment_results: Dict[str, float],
        learning_style: str = "visual",
        goals: Optional[List[str]] = None,
    ) -> LearningPath:
        """Create a personalized learning path for a student."""
        # Get student profile
        student = self._get_or_create_student(
            student_id,
            grade_level,
            learning_style,
        )

        # Analyze assessment results
        strengths, weaknesses = self._analyze_assessment(assessment_results)

        # Get curriculum topics for grade
        grade = GradeLevel(str(grade_level))
        topics = self.curriculum.get_topics_for_grade(grade)

        # Generate personalized lesson sequence
        lessons = self._generate_lesson_sequence(
            student,
            topics,
            strengths,
            weaknesses,
            goals or [],
        )

        # Create learning path
        path = LearningPath(
            id=f"path_{student_id}_{datetime.utcnow().timestamp()}",
            student_id=student_id,
            lessons=lessons,
            mastery_scores={topic: assessment_results.get(topic.value, 0.0) for topic in topics},
            recommended_topics=weaknesses[:3],  # Focus on top 3 weak areas
            learning_goals=goals or [],
            estimated_completion_date=self._estimate_completion_date(len(lessons)),
        )

        logger.info(f"Created learning path for student {student_id} with {len(lessons)} lessons")
        return path

    def _get_or_create_student(
        self,
        student_id: str,
        grade_level: int,
        learning_style: str,
    ) -> Student:
        """Get or create student profile."""
        # In production, fetch from database
        return Student(
            id=student_id,
            name="Student",
            grade_level=GradeLevel(str(grade_level)),
            age=grade_level + 5,  # Approximate age
            learning_style=LearningStyle(learning_style),
        )

    def _analyze_assessment(
        self,
        results: Dict[str, float],
    ) -> tuple[List[MathTopic], List[MathTopic]]:
        """Analyze assessment to identify strengths and weaknesses."""
        strengths = []
        weaknesses = []

        for topic_str, score in results.items():
            try:
                topic = MathTopic(topic_str)
                if score >= 0.8:
                    strengths.append(topic)
                elif score < 0.6:
                    weaknesses.append(topic)
            except ValueError:
                logger.warning(f"Unknown topic: {topic_str}")

        return strengths, weaknesses

    def _generate_lesson_sequence(
        self,
        student: Student,
        topics: List[MathTopic],
        strengths: List[MathTopic],
        weaknesses: List[MathTopic],
        goals: List[str],
    ) -> List[str]:
        """Generate personalized lesson sequence."""
        lessons = []

        # Start with prerequisite topics
        for topic in weaknesses:
            topic_lessons = self.curriculum.get_lessons_for_topic(
                topic,
                student.grade_level,
            )

            # Sort by difficulty
            topic_lessons.sort(key=lambda l: l.duration_minutes)

            # Add lessons based on student's learning style
            for lesson in topic_lessons[:2]:  # Max 2 lessons per weak topic
                lessons.append(lesson.id)

        # Add regular curriculum lessons
        for topic in topics:
            if topic not in weaknesses and topic not in strengths:
                topic_lessons = self.curriculum.get_lessons_for_topic(
                    topic,
                    student.grade_level,
                )
                if topic_lessons:
                    lessons.append(topic_lessons[0].id)

        # Add advanced lessons for strengths
        for topic in strengths:
            topic_lessons = self.curriculum.get_lessons_for_topic(
                topic,
                student.grade_level,
            )
            # Get more challenging lessons
            advanced_lessons = [l for l in topic_lessons if "advanced" in l.title.lower()]
            if advanced_lessons:
                lessons.append(advanced_lessons[0].id)

        return lessons

    def _estimate_completion_date(self, num_lessons: int) -> datetime:
        """Estimate completion date based on number of lessons."""
        # Assume 3 lessons per week
        weeks_needed = num_lessons / 3
        return datetime.utcnow() + timedelta(weeks=weeks_needed)

    def update_path(
        self,
        path: LearningPath,
        performance_data: Dict[str, float],
    ) -> LearningPath:
        """Update learning path based on performance."""
        # Update mastery scores
        for topic_str, score in performance_data.items():
            try:
                topic = MathTopic(topic_str)
                current_score = path.mastery_scores.get(topic, 0.0)
                # Weighted average with more weight on recent performance
                path.mastery_scores[topic] = 0.3 * current_score + 0.7 * score
            except ValueError:
                pass

        # Identify topics needing more practice
        struggling_topics = [
            topic
            for topic, score in path.mastery_scores.items()
            if score < settings.min_accuracy_for_advancement
        ]

        # Add remedial lessons if needed
        if struggling_topics:
            for topic in struggling_topics[:2]:  # Focus on top 2 struggling topics
                # Retrieve available lessons for the topic (difficulty filtering not supported in curriculum)
                remedial_lessons = self.curriculum.get_lessons_for_topic(topic)
                if remedial_lessons:
                    # Insert remedial lesson
                    path.lessons.insert(path.current_lesson + 1, remedial_lessons[0].id)
                    path.adaptive_adjustments.append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "action": "added_remedial",
                            "topic": topic.value,
                            "reason": f"mastery_score_{path.mastery_scores[topic]:.2f}",
                        }
                    )

        # Skip ahead if student is excelling
        excelling_topics = [topic for topic, score in path.mastery_scores.items() if score > 0.95]

        if len(excelling_topics) > len(path.mastery_scores) / 2:
            # Student is excelling, consider skipping some basic lessons
            path.adaptive_adjustments.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "accelerated_path",
                    "reason": "high_mastery_scores",
                }
            )

        path.updated_at = datetime.utcnow()
        return path

    def get_next_lesson(self, path: LearningPath) -> Optional[str]:
        """Get the next lesson in the learning path."""
        if path.current_lesson < len(path.lessons):
            return path.lessons[path.current_lesson]
        return None

    def complete_lesson(
        self,
        path: LearningPath,
        lesson_id: str,
        performance: float,
    ):
        """Mark a lesson as complete and update progress."""
        if lesson_id in path.lessons:
            path.progress[lesson_id] = performance

            # Move to next lesson if performance is sufficient
            if performance >= settings.min_accuracy_for_advancement:
                path.current_lesson += 1
            else:
                # Repeat lesson or add supplementary content
                logger.info(f"Student needs to repeat lesson {lesson_id}")

            path.updated_at = datetime.utcnow()
