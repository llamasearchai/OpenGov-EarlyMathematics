"""OpenAI Agents SDK integration for mathematics education."""

from typing import Any, Dict, List, Optional

from openai import OpenAI
from openai_agents_sdk.agents import Agent, RunContextWrapper
from openai_agents_sdk.models import ModelSettings
from openai_agents_sdk.tools import tool

from opengov_earlymathematics.config import settings
from opengov_earlymathematics.core.curriculum import Curriculum
from opengov_earlymathematics.core.learning_path import LearningPathGenerator
from opengov_earlymathematics.core.problem_engine import MathProblemSolver
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class MathAgent:
    """OpenAI Agents SDK powered mathematics education agent."""

    def __init__(self):
        """Initialize the math agent."""
        self.client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
        self.curriculum = Curriculum()
        self.problem_solver = MathProblemSolver()
        self.learning_path_generator = LearningPathGenerator()

        # Initialize the agent
        self.agent = Agent(
            name="MathEducationAgent",
            instructions=self._get_agent_instructions(),
            tools=[
                self.generate_problem,
                self.check_solution,
                self.explain_concept,
                self.create_learning_path,
                self.get_curriculum_info,
                self.assess_student_level,
            ],
            model_settings=ModelSettings(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
            ),
        )

    def _get_agent_instructions(self) -> str:
        """Get the agent system instructions."""
        return """
        You are an expert mathematics education AI agent designed to help K-12 students learn math.

        Your capabilities include:
        - Generating personalized math problems
        - Checking solutions with detailed feedback
        - Explaining mathematical concepts step-by-step
        - Creating adaptive learning paths
        - Providing curriculum information
        - Assessing student understanding

        Always be encouraging, patient, and supportive. Use age-appropriate language and provide multiple
        explanations when needed. Focus on building conceptual understanding rather than just getting
        correct answers.

        When students struggle, provide gentle hints and break down problems into smaller, manageable steps.
        Celebrate successes and maintain a positive, growth-oriented mindset.
        """

    @tool
    async def generate_problem(
        self,
        ctx: RunContextWrapper,
        topic: str,
        difficulty_level: int,
        student_level: int,
    ) -> Dict[str, Any]:
        """Generate a math problem for a student."""
        try:
            problem = self.problem_solver.generate_problem(
                topic=topic,
                difficulty_level=difficulty_level,
                student_level=student_level,
            )

            return {
                "success": True,
                "problem": {
                    "id": problem.id,
                    "question": problem.question,
                    "topic": problem.topic.value,
                    "difficulty": problem.difficulty.value,
                    "hints": problem.hints,
                },
            }
        except Exception as e:
            logger.error(f"Error generating problem: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    @tool
    async def check_solution(
        self,
        ctx: RunContextWrapper,
        problem_id: str,
        student_answer: str,
    ) -> Dict[str, Any]:
        """Check a student's solution and provide feedback."""
        try:
            result = self.problem_solver.check_solution(
                problem_id=problem_id,
                student_answer=student_answer,
                show_steps=True,
            )

            return {
                "success": True,
                "is_correct": result["correct"],
                "feedback": result["feedback"],
                "hint": result.get("hint"),
            }
        except Exception as e:
            logger.error(f"Error checking solution: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    @tool
    async def explain_concept(
        self,
        ctx: RunContextWrapper,
        concept: str,
        grade_level: int,
    ) -> Dict[str, Any]:
        """Explain a mathematical concept."""
        try:
            # Use AI to generate explanation
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Explain {concept} to a grade {grade_level} student using simple language, examples, and visual descriptions.",
                    },
                    {
                        "role": "user",
                        "content": f"Explain {concept} in a fun and easy way.",
                    },
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
            )

            explanation = response.choices[0].message.content

            return {
                "success": True,
                "explanation": explanation,
                "concept": concept,
                "grade_level": grade_level,
            }
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    @tool
    async def create_learning_path(
        self,
        ctx: RunContextWrapper,
        student_id: str,
        grade_level: int,
        assessment_results: Dict[str, float],
        learning_style: str = "visual",
    ) -> Dict[str, Any]:
        """Create a personalized learning path."""
        try:
            path = self.learning_path_generator.create_path(
                student_id=student_id,
                grade_level=grade_level,
                assessment_results=assessment_results,
                learning_style=learning_style,
            )

            return {
                "success": True,
                "path_id": path.id,
                "lessons": path.lessons,
                "recommended_topics": [topic.value for topic in path.recommended_topics],
                "estimated_completion": (
                    path.estimated_completion_date.isoformat()
                    if path.estimated_completion_date
                    else None
                ),
            }
        except Exception as e:
            logger.error(f"Error creating learning path: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    @tool
    async def get_curriculum_info(
        self,
        ctx: RunContextWrapper,
        grade_level: str,
    ) -> Dict[str, Any]:
        """Get curriculum information for a grade level."""
        try:
            from opengov_earlymathematics.core.models import GradeLevel

            grade = GradeLevel(grade_level)
            topics = self.curriculum.get_topics_for_grade(grade)

            return {
                "success": True,
                "grade_level": grade_level,
                "topics": [topic.value for topic in topics],
            }
        except Exception as e:
            logger.error(f"Error getting curriculum info: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    @tool
    async def assess_student_level(
        self,
        ctx: RunContextWrapper,
        student_id: str,
        responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Assess student level based on their responses."""
        try:
            # Analyze responses to determine strengths and weaknesses
            topic_scores = {}

            for response in responses:
                topic = response.get("topic")
                score = response.get("score", 0.5)

                if topic:
                    if topic not in topic_scores:
                        topic_scores[topic] = []
                    topic_scores[topic].append(score)

            # Calculate average scores
            assessment_results = {}
            for topic, scores in topic_scores.items():
                assessment_results[topic] = sum(scores) / len(scores)

            return {
                "success": True,
                "student_id": student_id,
                "assessment_results": assessment_results,
                "recommended_focus": list(assessment_results.keys())[
                    :3
                ],  # Top 3 topics to focus on
            }
        except Exception as e:
            logger.error(f"Error assessing student level: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def chat_with_student(
        self,
        student_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Chat with a student using the agent."""
        try:
            # Prepare context
            chat_context = context or {}
            chat_context["student_id"] = student_id

            # Run the agent
            response = await self.agent.run(
                message,
                context=chat_context,
            )

            return response.output
        except Exception as e:
            logger.error(f"Error in agent chat: {e}")
            return "I'm sorry, I encountered an error. Can you try asking again?"

    async def generate_lesson_plan(
        self,
        topic: str,
        grade_level: int,
        duration_minutes: int = 30,
    ) -> Dict[str, Any]:
        """Generate a lesson plan for a topic."""
        try:
            # Use agent to create lesson plan
            prompt = f"""
            Create a detailed lesson plan for {topic} at grade {grade_level}.
            Duration: {duration_minutes} minutes.

            Include:
            - Learning objectives
            - Materials needed
            - Step-by-step activities
            - Assessment methods
            - Differentiation strategies
            """

            response = await self.agent.run(prompt)

            return {
                "success": True,
                "lesson_plan": response.output,
                "topic": topic,
                "grade_level": grade_level,
                "duration": duration_minutes,
            }
        except Exception as e:
            logger.error(f"Error generating lesson plan: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def provide_adaptive_feedback(
        self,
        student_id: str,
        problem_id: str,
        student_answer: str,
        is_correct: bool,
        attempts: int,
    ) -> Dict[str, Any]:
        """Provide adaptive feedback based on student performance."""
        try:
            # Analyze the student's attempt pattern
            if is_correct:
                encouragement = "Excellent work! You really understand this concept."
                next_step = "You're ready to move on to more challenging problems."
            elif attempts == 1:
                encouragement = "Good try! Let me help you understand this better."
                next_step = "Let's break this down into smaller steps."
            elif attempts == 2:
                encouragement = "You're making progress! Don't give up."
                next_step = "Here's a hint to help you think about this differently."
            else:
                encouragement = "I can see you're working hard at this. Let's solve it together."
                next_step = "Let me show you the step-by-step solution."

            return {
                "success": True,
                "feedback": {
                    "encouragement": encouragement,
                    "next_step": next_step,
                    "hint": self._generate_hint_for_problem(problem_id, attempts),
                },
            }
        except Exception as e:
            logger.error(f"Error providing adaptive feedback: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _generate_hint_for_problem(self, problem_id: str, attempts: int) -> str:
        """Generate a hint for a problem based on attempt number."""
        hints = [
            "Think about what the problem is asking you to find.",
            "Try breaking the problem into smaller parts.",
            "Consider using a different approach or strategy.",
        ]

        hint_index = min(attempts - 1, len(hints) - 1)
        return hints[hint_index]
