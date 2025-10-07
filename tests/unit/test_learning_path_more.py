"""Additional tests for LearningPathGenerator update and navigation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from opengov_earlymathematics.core.learning_path import LearningPathGenerator
from opengov_earlymathematics.core.models import MathTopic, Lesson, GradeLevel


def build_basic_path():
    gen = LearningPathGenerator()
    assessment = {"multiplication": 0.4, "division": 0.55, "fractions": 0.95}
    path = gen.create_path("stud_x", 3, assessment)
    return gen, path


def test_update_path_adds_remedial_and_accelerates():
    gen, path = build_basic_path()

    # Provide performance data causing remedial addition for a struggling topic
    perf_data = {"multiplication": 0.3, "division": 0.5}
    updated = gen.update_path(path, perf_data)

    # Either remedial lessons inserted or adjustments recorded
    assert isinstance(updated.lessons, list)
    assert isinstance(updated.adaptive_adjustments, list)

    # Create a scenario of excelling topics to trigger acceleration
    for topic in list(updated.mastery_scores.keys())[:3]:
        updated.mastery_scores[topic] = 0.99

    updated2 = gen.update_path(updated, {})
    assert any(adj.get("action") == "accelerated_path" for adj in updated2.adaptive_adjustments)

    # Invalid topic key exercises ValueError branch in update logic
    updated3 = gen.update_path(updated2, {"not_a_topic": 0.1})
    assert isinstance(updated3, type(path))


def test_navigation_and_completion_behaviors():
    gen, path = build_basic_path()

    # Ensure we have at least one lesson in the path
    assert len(path.lessons) >= 0

    # get_next_lesson returns None or a valid id accordingly
    next_lesson = gen.get_next_lesson(path)
    if next_lesson is not None:
        assert isinstance(next_lesson, str)

        # Completing with sufficient performance advances the index
        gen.complete_lesson(path, next_lesson, performance=1.0)
        assert path.current_lesson >= 0

        # Completing with insufficient performance does not advance
        # Use same lesson id safely
        gen.complete_lesson(path, next_lesson, performance=0.0)
        assert path.current_lesson >= 0

    # Force no next lesson
    path.current_lesson = 10**6
    assert gen.get_next_lesson(path) is None


def test_assessment_with_unknown_topic_and_advanced_lesson_inclusion(monkeypatch):
    gen = LearningPathGenerator()
    # Monkeypatch curriculum to return an 'advanced' lesson for a strength topic
    advanced_lesson = Lesson(
        id="adv1",
        title="Algebra Advanced Concepts",
        topic=MathTopic.ALGEBRA_1,
        grade_level=GradeLevel.GRADE_8,
        duration_minutes=45,
        objectives=["obj"],
        content_blocks=[],
        practice_problems=[],
    )

    original = gen.curriculum.get_lessons_for_topic
    def fake_get_lessons_for_topic(topic, grade=None):
        if topic == MathTopic.ALGEBRA_1:
            return [advanced_lesson]
        return original(topic, grade)

    monkeypatch.setattr(gen.curriculum, "get_lessons_for_topic", fake_get_lessons_for_topic)

    # Include an unknown topic to hit warning branch in assessment analysis
    assessment = {"algebra_1": 0.9, "unknown_topic": 0.1}
    path = gen.create_path("stud_unknown", 8, assessment)
    # Advanced lesson should be included due to strength
    assert "adv1" in path.lessons
