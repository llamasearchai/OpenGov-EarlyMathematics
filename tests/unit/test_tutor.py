"""Unit tests for AI tutor functionality."""

import pytest
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from opengov_earlymathematics.ai.tutor import AITutor, MathProblemGenerator


class TestMathProblemGenerator:
    """Test math problem generator."""

    def test_init(self):
        """Test problem generator initialization."""
        generator = MathProblemGenerator()
        assert generator.client is not None

    @patch('opengov_earlymathematics.ai.tutor.OpenAI')
    def test_generate_problem_success(self, mock_openai):
        """Test successful problem generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"problem": "2+2", "solution": "4", "explanation": "Basic addition"}'
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        generator = MathProblemGenerator()
        result = generator.generate_problem("addition", 5, "easy")

        assert result["problem"] == "2+2"
        assert result["solution"] == "4"
        assert result["explanation"] == "Basic addition"

    @patch('opengov_earlymathematics.ai.tutor.OpenAI')
    def test_generate_problem_fallback(self, mock_openai):
        """Test fallback when OpenAI fails."""
        # Mock OpenAI to raise exception
        mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")

        generator = MathProblemGenerator()
        result = generator.generate_problem("addition", 5, "easy")

        assert "What is 2 + 2?" in result["problem"]
        assert result["solution"] == "4"


class TestAITutor:
    """Test AI tutor functionality."""

    def test_init(self):
        """Test AI tutor initialization."""
        tutor = AITutor("student_123")
        assert tutor.student_id == "student_123"
        assert tutor.client is not None
        assert tutor.problem_generator is not None
        assert tutor.conversation_history == []
        assert tutor.session_context["student_id"] == "student_123"

    @patch('opengov_earlymathematics.ai.tutor.OpenAI')
    def test_start_session(self, mock_openai):
        """Test starting a tutoring session."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Welcome! Let's learn addition."
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        tutor = AITutor("student_123")
        result = tutor.start_session("addition")

        assert result["session_id"] == "session_student_123_1"
        assert result["greeting"] == "Welcome! Let's learn addition."
        assert result["topic"] == "addition"
        assert len(tutor.conversation_history) == 1

    def test_provide_hint(self):
        """Test hint generation."""
        tutor = AITutor("student_123")
        hint = tutor.provide_hint("problem_1", 1)

        assert hint in [
            "Think about what the problem is asking. What do we need to find?",
            "Try breaking the problem into smaller steps. What's the first thing we should do?",
            "Look at the numbers carefully. Is there a pattern or relationship?",
        ]

    def test_explain_concept(self):
        """Test concept explanation."""
        tutor = AITutor("student_123")

        with patch.object(tutor.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Fractions are parts of a whole..."
            mock_create.return_value = mock_response

            explanation = tutor.explain_concept("fractions", 5)
            assert explanation == "Fractions are parts of a whole..."

    def test_generate_encouragement(self):
        """Test encouragement generation."""
        tutor = AITutor("student_123")

        # Test different contexts
        correct_msg = tutor.generate_encouragement("correct")
        assert correct_msg in [
            "Fantastic work! You're getting better at this!",
            "That's absolutely right! You're a math star!",
            "Excellent! You really understand this concept!",
            "Way to go! Your hard work is paying off!",
        ]

        incorrect_msg = tutor.generate_encouragement("incorrect")
        assert incorrect_msg in [
            "That's not quite right, but I love how you're thinking! Let's try again.",
            "Good try! Making mistakes is how we learn. Let's look at it differently.",
            "Almost there! You're on the right track. Want to try once more?",
            "Nice effort! Let's work through this together.",
        ]

        general_msg = tutor.generate_encouragement("general")
        assert general_msg in [
            "Keep up the great work! You're doing amazing!",
            "I'm so proud of how hard you're working!",
            "You're making excellent progress!",
            "Learning math is an adventure, and you're doing great!",
        ]

    def test_generate_problem(self):
        """Test problem generation through tutor."""
        tutor = AITutor("student_123")

        with patch.object(tutor.problem_generator, 'generate_problem') as mock_generate:
            mock_generate.return_value = {"problem": "2+2", "solution": "4", "explanation": "Basic"}
            result = tutor.generate_problem("addition", 5, "easy")

            assert result["problem"] == "2+2"
            mock_generate.assert_called_once_with("addition", 5, "easy")