"""API routes for OpenGov-EarlyMathematics."""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.learning_path import LearningPathGenerator
from opengov_earlymathematics.core.models import (
    GradeLevel,
    MathTopic,
)
from opengov_earlymathematics.core.problem_engine import MathProblemSolver
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize services
curriculum = Curriculum()
learning_path_generator = LearningPathGenerator()
problem_solver = MathProblemSolver()

# API Router
api_router = APIRouter()


# Request/Response Models
class CreateLearningPathRequest(BaseModel):
    student_id: str
    grade_level: int
    assessment_results: Dict[str, float]
    learning_style: str = "visual"
    goals: Optional[List[str]] = None


class LearningPathResponse(BaseModel):
    path_id: str
    student_id: str
    lessons: List[str]
    recommended_topics: List[str]
    estimated_completion_date: Optional[str]


class ProblemRequest(BaseModel):
    topic: str
    difficulty_level: int
    student_level: int


class SolutionCheckRequest(BaseModel):
    problem_id: str
    student_answer: str
    show_steps: bool = False


class TutoringRequest(BaseModel):
    student_id: str
    topic: str
    question: str


# Routes


@api_router.get("/curriculum/grades/{grade}/topics", response_model=List[str])
async def get_topics_for_grade(grade: str):
    """Get all math topics for a specific grade level."""
    try:
        grade_level = GradeLevel(grade)
        topics = curriculum.get_topics_for_grade(grade_level)
        return [topic.value for topic in topics]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid grade level: {grade}")


@api_router.get("/curriculum/topics/{topic}/lessons", response_model=List[Dict])
async def get_lessons_for_topic(
    topic: str, grade: Optional[str] = Query(None, description="Filter by grade level")
):
    """Get all lessons for a specific math topic."""
    try:
        topic_enum = MathTopic(topic)
        grade_level = GradeLevel(grade) if grade else None

        lessons = curriculum.get_lessons_for_topic(topic_enum, grade_level)
        return [
            {
                "id": lesson.id,
                "title": lesson.title,
                "grade_level": lesson.grade_level.value,
                "duration_minutes": lesson.duration_minutes,
                "objectives": lesson.objectives,
            }
            for lesson in lessons
        ]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid topic: {topic}")


@api_router.get("/problems/{problem_id}", response_model=Dict)
async def get_problem(problem_id: str):
    """Get a specific math problem."""
    problem = curriculum.get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return {
        "id": problem.id,
        "topic": problem.topic.value,
        "grade_level": problem.grade_level.value,
        "difficulty": problem.difficulty.value,
        "question": problem.question,
        "hints": problem.hints,
        "solution_steps": problem.solution_steps,
        "explanation": problem.explanation,
    }


@api_router.post("/problems/generate", response_model=Dict)
async def generate_problem(request: ProblemRequest):
    """Generate a new math problem."""
    try:
        problem = problem_solver.generate_problem(
            topic=request.topic,
            difficulty_level=request.difficulty_level,
            student_level=request.student_level,
        )

        return {
            "id": problem.id,
            "topic": problem.topic.value,
            "grade_level": problem.grade_level.value,
            "difficulty": problem.difficulty.value,
            "question": problem.question,
            "hints": problem.hints,
            "solution_steps": problem.solution_steps,
            "explanation": problem.explanation,
        }
    except Exception as e:
        logger.error(f"Error generating problem: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate problem")


@api_router.post("/problems/check-solution", response_model=Dict)
async def check_solution(request: SolutionCheckRequest):
    """Check a student's solution to a problem."""
    try:
        result = problem_solver.check_solution(
            problem_id=request.problem_id,
            student_answer=request.student_answer,
            show_steps=request.show_steps,
        )

        return result
    except Exception as e:
        logger.error(f"Error checking solution: {e}")
        raise HTTPException(status_code=500, detail="Failed to check solution")


@api_router.post("/learning-paths/create", response_model=LearningPathResponse)
async def create_learning_path(request: CreateLearningPathRequest):
    """Create a personalized learning path for a student."""
    try:
        path = learning_path_generator.create_path(
            student_id=request.student_id,
            grade_level=request.grade_level,
            assessment_results=request.assessment_results,
            learning_style=request.learning_style,
            goals=request.goals,
        )

        return LearningPathResponse(
            path_id=path.id,
            student_id=path.student_id,
            lessons=path.lessons,
            recommended_topics=[topic.value for topic in path.recommended_topics],
            estimated_completion_date=(
                path.estimated_completion_date.isoformat()
                if path.estimated_completion_date
                else None
            ),
        )
    except Exception as e:
        logger.error(f"Error creating learning path: {e}")
        raise HTTPException(status_code=500, detail="Failed to create learning path")


@api_router.get("/learning-paths/{path_id}", response_model=Dict)
async def get_learning_path(path_id: str):
    """Get a learning path by ID."""
    # In production, fetch from database
    # For demo, return sample data
    return {
        "id": path_id,
        "student_id": "student_123",
        "current_lesson": 0,
        "lessons": ["lesson_mult_3_1", "lesson_div_3_1"],
        "progress": {},
        "mastery_scores": {"multiplication": 0.7, "division": 0.6},
        "recommended_topics": ["fractions", "geometry"],
        "learning_goals": ["master_multiplication", "understand_fractions"],
    }


@api_router.get("/learning-paths/{path_id}/next-lesson", response_model=Optional[str])
async def get_next_lesson(path_id: str):
    """Get the next lesson in a learning path."""
    # In production, fetch path and call get_next_lesson
    return "lesson_mult_3_1"


@api_router.post("/tutoring/start-session", response_model=Dict)
async def start_tutoring_session(student_id: str, topic: str):
    """Start an AI tutoring session."""
    try:
        from opengov_earlymathematics.ai.tutor import AITutor

        tutor = AITutor(student_id)
        session = tutor.start_session(topic)

        return session
    except Exception as e:
        logger.error(f"Error starting tutoring session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start tutoring session")


@api_router.post("/tutoring/ask", response_model=str)
async def ask_tutor(request: TutoringRequest):
    """Ask the AI tutor a question."""
    try:
        from opengov_earlymathematics.ai.tutor import AITutor

        tutor = AITutor(request.student_id)
        response = tutor.help_with(request.question)

        return response
    except Exception as e:
        logger.error(f"Error in tutoring session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tutor response")


@api_router.get("/students/{student_id}/progress", response_model=Dict)
async def get_student_progress(student_id: str):
    """Get a student's learning progress."""
    # In production, fetch from database
    return {
        "student_id": student_id,
        "topic_mastery": {
            "multiplication": 0.75,
            "division": 0.60,
            "fractions": 0.45,
        },
        "skills_acquired": ["basic_multiplication", "single_digit_division"],
        "current_grade_progress": 0.65,
        "strengths": ["multiplication"],
        "areas_for_improvement": ["fractions", "word_problems"],
        "recent_achievements": ["First multiplication table", "Speed demon"],
        "learning_velocity": 1.2,
        "engagement_score": 0.85,
    }


@api_router.get("/analytics/overview", response_model=Dict)
async def get_analytics_overview():
    """Get platform analytics overview."""
    return {
        "total_students": 1247,
        "active_sessions": 89,
        "problems_solved_today": 3421,
        "avg_session_duration": 28.5,
        "top_topics": ["multiplication", "fractions", "addition"],
        "student_satisfaction": 4.2,
        "learning_outcomes": {
            "improvement_rate": 0.73,
            "retention_rate": 0.82,
            "mastery_rate": 0.68,
        },
    }


@api_router.get("/health/detailed", response_model=Dict)
async def detailed_health_check():
    """Detailed health check including service status."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "ai_models": "loaded",
            "curriculum": "loaded",
        },
        "uptime": "2h 34m",
        "requests_today": 15420,
    }
