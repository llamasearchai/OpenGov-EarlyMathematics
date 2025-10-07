"""Ollama integration for local LLM operations."""

import asyncio
import json
from typing import Any, Dict, List, Optional

import ollama

from opengov_earlymathematics.config import settings
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaMathClient:
    """Ollama client for local mathematics education operations."""

    def __init__(self):
        """Initialize Ollama client."""
        self.client = ollama.Client()
        self.available_models = []
        self._check_ollama_status()

    def _check_ollama_status(self) -> bool:
        """Check if Ollama is running and available."""
        try:
            # Try to list available models
            models = self.client.list()
            self.available_models = [model["name"] for model in models.get("models", [])]
            logger.info(f"Ollama models available: {self.available_models}")
            return True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        return len(self.available_models) > 0

    def pull_model(self, model_name: str = "llama2") -> bool:
        """Pull a model from Ollama."""
        try:
            logger.info(f"Pulling model: {model_name}")
            self.client.pull(model_name)
            self.available_models.append(model_name)
            return True
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False

    def generate_response(
        self,
        prompt: str,
        model: str = "llama2",
        context: Optional[str] = None,
    ) -> str:
        """Generate a response using Ollama."""
        try:
            if model not in self.available_models:
                logger.warning(f"Model {model} not available, pulling...")
                if not self.pull_model(model):
                    return "Sorry, I couldn't load the required model."

            response = self.client.generate(
                model=model,
                prompt=prompt,
                context=context,
                options={
                    "temperature": settings.openai_temperature,
                    "num_predict": settings.openai_max_tokens,
                },
            )

            return response.get("response", "No response generated.")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I encountered an error. Please try again."

    def chat_with_student(
        self,
        student_id: str,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Chat with a student using Ollama."""
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    context += f"{msg['role']}: {msg['message']}\n"

            # Create educational prompt
            system_prompt = """
            You are a friendly and patient math tutor helping K-12 students.
            Use simple language, be encouraging, and explain concepts step by step.
            Focus on building understanding rather than just giving answers.
            """

            full_prompt = f"{system_prompt}\n\nConversation:\n{context}\nStudent: {message}\nTutor:"

            return self.generate_response(full_prompt)
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I'm having trouble responding right now. Please try again."

    def explain_math_concept(
        self,
        concept: str,
        grade_level: int,
        learning_style: str = "visual",
    ) -> str:
        """Explain a math concept using Ollama."""
        try:
            prompt = f"""
            Explain {concept} to a grade {grade_level} student.
            Use {learning_style} learning style.
            Be encouraging and use simple examples.
            Break it down into small, easy-to-understand steps.
            """

            return self.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return f"Let me explain {concept} in a simple way..."

    def generate_practice_problem(
        self,
        topic: str,
        difficulty: str,
        grade_level: int,
    ) -> Dict[str, Any]:
        """Generate a practice problem using Ollama."""
        try:
            prompt = f"""
            Generate a {difficulty} level {topic} problem for grade {grade_level}.
            Return the response in JSON format with:
            - question: the problem text
            - answer: the correct answer
            - explanation: step-by-step solution
            - hints: 2-3 helpful hints
            """

            response = self.generate_response(prompt)

            try:
                # Try to parse as JSON
                problem_data = json.loads(response)
                return {
                    "success": True,
                    "problem": problem_data,
                }
            except json.JSONDecodeError:
                # If not JSON, create structured response
                return {
                    "success": True,
                    "problem": {
                        "question": response,
                        "answer": "Please check with teacher",
                        "explanation": "Generated using AI tutor",
                        "hints": ["Think step by step", "Use what you know"],
                    },
                }
        except Exception as e:
            logger.error(f"Error generating problem: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def assess_student_response(
        self,
        problem: str,
        student_answer: str,
        correct_answer: str,
    ) -> Dict[str, Any]:
        """Assess a student's response."""
        try:
            prompt = f"""
            Problem: {problem}
            Correct answer: {correct_answer}
            Student answer: {student_answer}

            Analyze the student's response:
            - Is it correct? (yes/no)
            - What did they do well?
            - What mistakes did they make?
            - What should they focus on next?

            Return response as JSON with: correct, feedback, encouragement, next_steps
            """

            response = self.generate_response(prompt)

            try:
                assessment = json.loads(response)
                return {
                    "success": True,
                    "assessment": assessment,
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "assessment": {
                        "correct": student_answer == correct_answer,
                        "feedback": response,
                        "encouragement": "Keep trying!",
                        "next_steps": "Review the concept and try again.",
                    },
                }
        except Exception as e:
            logger.error(f"Error assessing response: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def create_lesson_summary(
        self,
        topic: str,
        key_points: List[str],
        grade_level: int,
    ) -> str:
        """Create a lesson summary."""
        try:
            points_text = "\n".join(f"- {point}" for point in key_points)

            prompt = f"""
            Create a clear, engaging summary for a grade {grade_level} math lesson on {topic}.

            Key points covered:
            {points_text}

            Make it encouraging and highlight the most important concepts.
            """

            return self.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error creating lesson summary: {e}")
            return f"Great job learning about {topic}! Remember the key points we covered."

    def suggest_next_topics(
        self,
        current_topic: str,
        student_progress: Dict[str, float],
        grade_level: int,
    ) -> List[str]:
        """Suggest next topics based on progress."""
        try:
            progress_text = "\n".join(
                f"- {topic}: {score*100:.0f}%" for topic, score in student_progress.items()
            )

            prompt = f"""
            Current topic: {current_topic}
            Student progress:
            {progress_text}

            Suggest 3-4 next math topics for grade {grade_level} that build on what they've learned.
            Consider their progress levels and suggest appropriate difficulty progression.
            Return as a simple list.
            """

            response = self.generate_response(prompt)

            # Extract topics from response
            lines = response.split("\n")
            topics = []
            for line in lines:
                line = line.strip()
                if line.startswith("-") or line.startswith("*") or line.isdigit():
                    topic = line.lstrip("-*123456789. ").strip()
                    if topic and len(topic) > 3:
                        topics.append(topic)

            return topics[:4]  # Return up to 4 topics
        except Exception as e:
            logger.error(f"Error suggesting next topics: {e}")
            return ["Practice current topic", "Review fundamentals"]

    def generate_study_plan(
        self,
        student_goals: List[str],
        available_time: int,  # minutes per day
        grade_level: int,
    ) -> str:
        """Generate a personalized study plan."""
        try:
            goals_text = "\n".join(f"- {goal}" for goal in student_goals)

            prompt = f"""
            Create a daily study plan for a grade {grade_level} student.
            Available time: {available_time} minutes per day
            Goals: {goals_text}

            Make a realistic, encouraging plan that includes:
            - Warm-up activities
            - Main learning activities
            - Practice problems
            - Review and reflection
            - Breaks

            Keep sessions engaging and not overwhelming.
            """

            return self.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            return "Focus on one concept at a time and practice regularly!"

    async def embed_text(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """Generate embeddings for text using Ollama."""
        try:
            if model not in self.available_models:
                if not self.pull_model(model):
                    logger.warning(f"Could not pull embedding model {model}")
                    return []

            response = self.client.embeddings(model=model, prompt=text)
            return response.get("embedding", [])
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []

    def find_similar_problems(
        self,
        target_problem: str,
        problem_bank: List[str],
        top_k: int = 5,
    ) -> List[str]:
        """Find similar problems using embeddings."""
        try:
            # Generate embedding for target problem
            target_embedding = asyncio.run(self.embed_text(target_problem))

            if not target_embedding:
                return []

            # Generate embeddings for problem bank
            similarities = []
            for problem in problem_bank:
                problem_embedding = asyncio.run(self.embed_text(problem))

                if problem_embedding:
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(target_embedding, problem_embedding)
                    similarities.append((problem, similarity))

            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [problem for problem, _ in similarities[:top_k]]
        except Exception as e:
            logger.error(f"Error finding similar problems: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np

            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)

            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models."""
        return {
            "available": self.is_available(),
            "models": self.available_models,
            "recommended_models": {
                "chat": "llama2",
                "coding": "codellama",
                "embeddings": "nomic-embed-text",
            },
        }
