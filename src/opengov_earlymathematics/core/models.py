"""Core data models for the education platform."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GradeLevel(str, Enum):
    """Grade level enumeration."""

    KINDERGARTEN = "K"
    GRADE_1 = "1"
    GRADE_2 = "2"
    GRADE_3 = "3"
    GRADE_4 = "4"
    GRADE_5 = "5"
    GRADE_6 = "6"
    GRADE_7 = "7"
    GRADE_8 = "8"
    GRADE_9 = "9"
    GRADE_10 = "10"
    GRADE_11 = "11"
    GRADE_12 = "12"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningStyle(str, Enum):
    """Learning style enumeration."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class MathTopic(str, Enum):
    """Mathematics topic enumeration."""

    # Early Math
    COUNTING = "counting"
    NUMBER_RECOGNITION = "number_recognition"
    BASIC_ADDITION = "basic_addition"
    BASIC_SUBTRACTION = "basic_subtraction"
    SHAPES = "shapes"
    PATTERNS = "patterns"
    MEASUREMENT = "measurement"
    TIME = "time"
    MONEY = "money"

    # Elementary
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    FRACTIONS = "fractions"
    DECIMALS = "decimals"
    GEOMETRY = "geometry"
    DATA_GRAPHS = "data_graphs"
    WORD_PROBLEMS = "word_problems"

    # Middle School
    PRE_ALGEBRA = "pre_algebra"
    RATIOS = "ratios"
    PROPORTIONS = "proportions"
    STATISTICS = "statistics"
    PROBABILITY = "probability"
    COORDINATE_GEOMETRY = "coordinate_geometry"
    ALGEBRAIC_THINKING = "algebraic_thinking"

    # High School
    ALGEBRA_1 = "algebra_1"
    ALGEBRA_2 = "algebra_2"
    GEOMETRY_ADVANCED = "geometry_advanced"
    TRIGONOMETRY = "trigonometry"
    PRE_CALCULUS = "pre_calculus"
    CALCULUS = "calculus"


class Student(BaseModel):
    """Student model."""

    id: str = Field(description="Student ID")
    name: str = Field(description="Student name")
    email: Optional[str] = Field(default=None, description="Email address")
    grade_level: GradeLevel = Field(description="Current grade level")
    age: int = Field(ge=3, le=18, description="Student age")
    learning_style: LearningStyle = Field(default=LearningStyle.VISUAL)
    parent_email: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    total_practice_time: int = Field(default=0, description="Total practice time in minutes")
    points: int = Field(default=0, description="Gamification points")
    current_streak: int = Field(default=0, description="Current practice streak in days")
    achievements: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class Teacher(BaseModel):
    """Teacher model."""

    id: str = Field(description="Teacher ID")
    name: str = Field(description="Teacher name")
    email: str = Field(description="Email address")
    subjects: List[MathTopic] = Field(description="Subjects taught")
    grade_levels: List[GradeLevel] = Field(description="Grade levels taught")
    experience_years: int = Field(ge=0, description="Years of experience")
    rating: float = Field(ge=0.0, le=5.0, default=0.0)
    total_sessions: int = Field(default=0)
    specializations: List[str] = Field(default_factory=list)
    availability: Dict[str, List[str]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Problem(BaseModel):
    """Math problem model."""

    id: str = Field(description="Problem ID")
    topic: MathTopic = Field(description="Math topic")
    grade_level: GradeLevel = Field(description="Grade level")
    difficulty: DifficultyLevel = Field(description="Difficulty level")
    question: str = Field(description="Problem question")
    answer: str = Field(description="Correct answer")
    solution_steps: List[str] = Field(description="Step-by-step solution")
    hints: List[str] = Field(default_factory=list, description="Problem hints")
    visual_aids: List[str] = Field(default_factory=list, description="URLs to visual aids")
    prerequisites: List[MathTopic] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    explanation: str = Field(description="Detailed explanation")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Lesson(BaseModel):
    """Lesson model."""

    id: str = Field(description="Lesson ID")
    title: str = Field(description="Lesson title")
    topic: MathTopic = Field(description="Math topic")
    grade_level: GradeLevel = Field(description="Grade level")
    duration_minutes: int = Field(description="Estimated duration")
    objectives: List[str] = Field(description="Learning objectives")
    content_blocks: List[Dict[str, Any]] = Field(description="Lesson content")
    practice_problems: List[str] = Field(description="Problem IDs")
    assessment: Optional[str] = Field(default=None, description="Assessment ID")
    resources: List[str] = Field(default_factory=list)
    interactive_elements: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LearningPath(BaseModel):
    """Personalized learning path model."""

    id: str = Field(description="Path ID")
    student_id: str = Field(description="Student ID")
    current_lesson: int = Field(default=0)
    lessons: List[str] = Field(description="Ordered list of lesson IDs")
    progress: Dict[str, float] = Field(default_factory=dict)
    mastery_scores: Dict[MathTopic, float] = Field(default_factory=dict)
    recommended_topics: List[MathTopic] = Field(default_factory=list)
    learning_goals: List[str] = Field(default_factory=list)
    estimated_completion_date: Optional[datetime] = None
    adaptive_adjustments: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """Learning session model."""

    id: str = Field(description="Session ID")
    student_id: str = Field(description="Student ID")
    teacher_id: Optional[str] = Field(default=None, description="Teacher ID")
    lesson_id: Optional[str] = Field(default=None, description="Lesson ID")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(default=0)
    problems_attempted: int = Field(default=0)
    problems_correct: int = Field(default=0)
    hints_used: int = Field(default=0)
    points_earned: int = Field(default=0)
    topics_covered: List[MathTopic] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    feedback: Optional[str] = None
    recording_url: Optional[str] = None


class Assessment(BaseModel):
    """Assessment model."""

    id: str = Field(description="Assessment ID")
    title: str = Field(description="Assessment title")
    type: str = Field(description="Assessment type (quiz, test, diagnostic)")
    grade_level: GradeLevel = Field(description="Grade level")
    topics: List[MathTopic] = Field(description="Topics covered")
    problems: List[str] = Field(description="Problem IDs")
    time_limit_minutes: Optional[int] = None
    passing_score: float = Field(ge=0.0, le=1.0, default=0.7)
    allow_retries: bool = Field(default=True)
    max_retries: int = Field(default=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Progress(BaseModel):
    """Student progress model."""

    student_id: str = Field(description="Student ID")
    topic_mastery: Dict[MathTopic, float] = Field(default_factory=dict)
    skills_acquired: List[str] = Field(default_factory=list)
    current_grade_progress: float = Field(ge=0.0, le=1.0, default=0.0)
    strengths: List[MathTopic] = Field(default_factory=list)
    areas_for_improvement: List[MathTopic] = Field(default_factory=list)
    recent_achievements: List[str] = Field(default_factory=list)
    learning_velocity: float = Field(default=1.0, description="Learning speed multiplier")
    engagement_score: float = Field(ge=0.0, le=1.0, default=0.5)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
