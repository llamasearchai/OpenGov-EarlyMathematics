"""AI-powered tutoring system."""

import json
from typing import Any, Dict, List

from openai import OpenAI

from opengov_earlymathematics.config import settings
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class MathProblemGenerator:
    """Generate math problems for students."""

    def __init__(self):
        """Initialize problem generator."""
        self.client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

    def generate_problem(
        self, topic: str, grade_level: int, difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """Generate a math problem."""
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Generate a {difficulty} {topic} math problem for grade {grade_level}. Return as JSON with 'problem', 'solution', and 'explanation' fields.",
                    }
                ],
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content
            if content:
                # Try to parse as JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback if not JSON
                    return {
                        "problem": content,
                        "solution": "Solution not available",
                        "explanation": "Please work through this problem step by step.",
                    }

        except Exception as e:
            logger.error(f"Error generating problem: {e}")

        # Fallback problem
        return {
            "problem": f"What is 2 + 2? (Grade {grade_level} {topic})",
            "solution": "4",
            "explanation": "Basic addition: 2 + 2 equals 4.",
        }


class AITutor:
    """AI-powered mathematics tutor."""

    def __init__(self, student_id: str):
        """Initialize AI tutor for a student."""
        self.student_id = student_id
        self.client = OpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
        )
        self.problem_generator = MathProblemGenerator()
        self.conversation_history: List[Dict[str, str]] = []
        self.session_context = {
            "student_id": student_id,
            "topics_covered": [],
            "problems_solved": 0,
            "hints_given": 0,
        }

    def start_session(self, topic: str) -> Dict[str, Any]:
        """Start a tutoring session."""
        self.session_context["current_topic"] = topic

        greeting = self._generate_greeting(topic)

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": greeting,
            }
        )

        return {
            "session_id": f"session_{self.student_id}_{len(self.conversation_history)}",
            "greeting": greeting,
            "topic": topic,
        }

    def help_with(self, question: str) -> str:
        """Provide help with a specific question."""
        # Add student question to history
        self.conversation_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        # Generate response
        response = self._generate_response(question)

        # Add response to history
        self.conversation_history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        return response

    def _generate_greeting(self, topic: str) -> str:
        """Generate a friendly greeting."""
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly, patient, and encouraging math tutor for K-12 students. "
                            "Use simple, age-appropriate language. Be enthusiastic and supportive. "
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Start a tutoring session on {topic}. Greet the student warmly and briefly introduce what we'll learn.",
                    },
                ],
                temperature=settings.openai_temperature,
                max_tokens=200,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return f"Hi! Today we're going to learn about {topic}. This is going to be fun!"

    def _generate_response(self, question: str) -> str:
        """Generate AI response to student question."""
        try:
            # Build context
            system_prompt = self._build_system_prompt()

            # Include recent history for context
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            # Add last 5 messages for context
            for msg in self.conversation_history[-5:]:
                messages.append(msg)

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Let me think about that... Can you try explaining what part you find confusing?"

    def _build_system_prompt(self) -> str:
        """Build system prompt for AI."""
        topic = self.session_context.get("current_topic", "mathematics")

        return f"""
        You are an expert math tutor helping a K-12 student with {topic}.

        Guidelines:
        1. Use simple, clear explanations appropriate for young students
        2. Break down complex concepts into small, manageable steps
        3. Use visual descriptions and real-world examples
        4. Be encouraging and patient - never make the student feel bad
        5. If they're struggling, provide gentle hints rather than direct answers
        6. Use analogies and stories to make concepts memorable
        7. Celebrate their successes with enthusiasm
        8. Ask guiding questions to help them think through problems

        Teaching approach:
        - Start with concrete examples before abstract concepts
        - Use the "I do, We do, You do" method
        - Provide multiple representations (visual, verbal, symbolic)
        - Connect to what they already know

        Remember: Your goal is to help them understand, not just get the right answer.
        """

    def provide_hint(self, problem_id: str, hint_level: int = 1) -> str:
        """Provide a hint for a problem."""
        self.session_context["hints_given"] += 1

        # Generate appropriate hint based on level
        hints = [
            "Think about what the problem is asking. What do we need to find?",
            "Try breaking the problem into smaller steps. What's the first thing we should do?",
            "Look at the numbers carefully. Is there a pattern or relationship?",
        ]

        if hint_level <= len(hints):
            return hints[hint_level - 1]

        return "Let's work through this together step by step!"

    def explain_concept(self, concept: str, grade_level: int) -> str:
        """Explain a mathematical concept."""
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Explain {concept} to a grade {grade_level} student using simple language, examples, and visuals.",
                    },
                    {
                        "role": "user",
                        "content": f"Explain {concept} in a fun and easy way.",
                    },
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return f"Let me explain {concept} in a simple way..."

    def generate_encouragement(self, context: str = "general") -> str:
        """Generate encouraging message."""
        encouragements = {
            "correct": [
                "Fantastic work! You're getting better at this!",
                "That's absolutely right! You're a math star!",
                "Excellent! You really understand this concept!",
                "Way to go! Your hard work is paying off!",
            ],
            "incorrect": [
                "That's not quite right, but I love how you're thinking! Let's try again.",
                "Good try! Making mistakes is how we learn. Let's look at it differently.",
                "Almost there! You're on the right track. Want to try once more?",
                "Nice effort! Let's work through this together.",
            ],
            "general": [
                "Keep up the great work! You're doing amazing!",
                "I'm so proud of how hard you're working!",
                "You're making excellent progress!",
                "Learning math is an adventure, and you're doing great!",
            ],
        }

        import random

        return random.choice(encouragements.get(context, encouragements["general"]))

    def generate_problem(
        self, topic: str, grade_level: int, difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """Generate a new math problem."""
        return self.problem_generator.generate_problem(topic, grade_level, difficulty)
