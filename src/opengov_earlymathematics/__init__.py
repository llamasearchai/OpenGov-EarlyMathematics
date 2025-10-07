"""OpenGov Early Mathematics - AI-powered K-12 mathematics education platform."""

__version__ = "1.0.0"
__author__ = "OpenGov Early Mathematics Team"
__description__ = "AI-powered mathematics learning platform for K-12 education"

from .ai.tutor import AITutor
from .core.models import MathTopic, Student

__all__ = [
    "AITutor",
    "MathTopic",
    "Student",
]
