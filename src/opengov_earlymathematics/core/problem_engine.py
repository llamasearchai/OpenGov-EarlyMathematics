"""Mathematics problem generation and solving engine."""

import random
import re
from typing import Any, Dict, List

from opengov_earlymathematics.core.models import (
    DifficultyLevel,
    GradeLevel,
    MathTopic,
    Problem,
)
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class MathProblemSolver:
    """Generate and solve mathematics problems."""

    def __init__(self):
        """Initialize problem solver."""
        self.generators = {
            MathTopic.BASIC_ADDITION: self._generate_addition,
            MathTopic.BASIC_SUBTRACTION: self._generate_subtraction,
            MathTopic.MULTIPLICATION: self._generate_multiplication,
            MathTopic.DIVISION: self._generate_division,
            MathTopic.FRACTIONS: self._generate_fractions,
            MathTopic.ALGEBRA_1: self._generate_algebra,
        }

    def generate_problem(
        self,
        topic: str,
        difficulty_level: int,
        student_level: int,
    ) -> Problem:
        """Generate a math problem based on parameters."""
        topic_enum = MathTopic(topic)
        difficulty = DifficultyLevel(
            ["beginner", "intermediate", "advanced", "expert"][difficulty_level - 1]
        )
        grade = GradeLevel(str(student_level))

        # Get appropriate generator
        generator = self.generators.get(topic_enum, self._generate_default)

        # Generate problem
        problem_data = generator(difficulty)

        return Problem(
            id=f"prob_{topic}_{random.randint(1000, 9999)}",
            topic=topic_enum,
            grade_level=grade,
            difficulty=difficulty,
            **problem_data,
        )

    def _generate_addition(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate addition problems."""
        if difficulty == DifficultyLevel.BEGINNER:
            a, b = random.randint(1, 10), random.randint(1, 10)
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            a, b = random.randint(10, 50), random.randint(10, 50)
        elif difficulty == DifficultyLevel.ADVANCED:
            a, b = random.randint(50, 100), random.randint(50, 100)
        else:
            a, b = random.randint(100, 1000), random.randint(100, 1000)

        answer = str(a + b)

        return {
            "question": f"What is {a} + {b}?",
            "answer": answer,
            "solution_steps": [
                f"We need to add {a} and {b}",
                f"Starting with {a}",
                f"Adding {b}",
                f"{a} + {b} = {answer}",
            ],
            "hints": [
                "Line up the numbers vertically",
                "Start adding from the ones place",
                f"Think: what do you get when you combine {a} and {b}?",
            ],
            "explanation": f"Addition combines two numbers. {a} plus {b} equals {answer}.",
        }

    def _generate_subtraction(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate subtraction problems."""
        if difficulty == DifficultyLevel.BEGINNER:
            a, b = random.randint(5, 20), random.randint(1, 10)
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            a, b = random.randint(20, 100), random.randint(10, 50)
        else:
            a, b = random.randint(100, 1000), random.randint(50, 500)

        # Ensure positive result
        a, b = max(a, b), min(a, b)
        answer = str(a - b)

        return {
            "question": f"What is {a} - {b}?",
            "answer": answer,
            "solution_steps": [
                f"We need to subtract {b} from {a}",
                f"Starting with {a}",
                f"Taking away {b}",
                f"{a} - {b} = {answer}",
            ],
            "hints": [
                "Think of subtraction as taking away",
                f"Start with {a} and remove {b}",
                "You can use a number line to help",
            ],
            "explanation": f"Subtraction finds the difference. {a} minus {b} equals {answer}.",
        }

    def _generate_multiplication(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate multiplication problems."""
        if difficulty == DifficultyLevel.BEGINNER:
            a, b = random.randint(1, 5), random.randint(1, 5)
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            a, b = random.randint(2, 10), random.randint(2, 10)
        else:
            a, b = random.randint(5, 20), random.randint(5, 20)

        answer = str(a * b)

        return {
            "question": f"What is {a} × {b}?",
            "answer": answer,
            "solution_steps": [
                f"We need to multiply {a} by {b}",
                f"This means {a} groups of {b}",
                f"Or adding {b} to itself {a} times",
                f"{a} × {b} = {answer}",
            ],
            "hints": [
                f"Think of {a} groups with {b} items in each",
                f"You can add {b} + {b} + ... ({a} times)",
                "Draw an array to visualize",
            ],
            "explanation": f"Multiplication is repeated addition. {a} times {b} equals {answer}.",
        }

    def _generate_division(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate division problems."""
        if difficulty == DifficultyLevel.BEGINNER:
            b = random.randint(1, 5)
            a = b * random.randint(1, 5)
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            b = random.randint(2, 10)
            a = b * random.randint(2, 10)
        else:
            b = random.randint(5, 20)
            a = b * random.randint(5, 20)

        answer = str(a // b)

        return {
            "question": f"What is {a} ÷ {b}?",
            "answer": answer,
            "solution_steps": [
                f"We need to divide {a} by {b}",
                f"How many groups of {b} fit in {a}?",
                f"Or: If we share {a} items among {b} groups equally",
                f"{a} ÷ {b} = {answer}",
            ],
            "hints": [
                f"Think: how many {b}s are in {a}?",
                "Division is the opposite of multiplication",
                f"Try: {b} × ? = {a}",
            ],
            "explanation": f"Division splits a number into equal groups. {a} divided by {b} equals {answer}.",
        }

    def _generate_fractions(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate fraction problems."""
        if difficulty == DifficultyLevel.BEGINNER:
            # Simple fractions
            numerator = random.randint(1, 5)
            denominator = random.randint(2, 10)
            question = f"Simplify the fraction {numerator}/{denominator}"

            # Find GCD and simplify
            from math import gcd

            g = gcd(numerator, denominator)
            simple_num = numerator // g
            simple_den = denominator // g
            answer = f"{simple_num}/{simple_den}"
        else:
            # Fraction operations
            n1, d1 = random.randint(1, 5), random.randint(2, 8)
            n2, d2 = random.randint(1, 5), random.randint(2, 8)
            question = f"What is {n1}/{d1} + {n2}/{d2}?"

            # Calculate sum
            from math import gcd

            lcm = (d1 * d2) // gcd(d1, d2)
            sum_num = (n1 * lcm // d1) + (n2 * lcm // d2)
            g = gcd(sum_num, lcm)
            answer = f"{sum_num // g}/{lcm // g}"

        return {
            "question": question,
            "answer": answer,
            "solution_steps": [
                "Identify the numerator and denominator",
                "Find common factors if simplifying",
                "Or find common denominator if adding",
                f"The answer is {answer}",
            ],
            "hints": [
                "Look for common factors",
                "Remember to simplify your answer",
                "Use visual aids like pie charts",
            ],
            "explanation": "Fractions represent parts of a whole.",
        }

    def _generate_algebra(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate algebra problems."""
        if difficulty == DifficultyLevel.BEGINNER:
            a = random.randint(1, 10)
            b = random.randint(1, 20)
            question = f"Solve for x: x + {a} = {b}"
            answer = str(b - a)
            steps = [
                f"We have x + {a} = {b}",
                f"Subtract {a} from both sides",
                f"x = {b} - {a}",
                f"x = {answer}",
            ]
        else:
            a = random.randint(2, 10)
            b = random.randint(10, 50)
            question = f"Solve for x: {a}x = {b}"
            answer = str(b / a if b % a == 0 else f"{b}/{a}")
            steps = [
                f"We have {a}x = {b}",
                f"Divide both sides by {a}",
                f"x = {b}/{a}",
                f"x = {answer}",
            ]

        return {
            "question": question,
            "answer": answer,
            "solution_steps": steps,
            "hints": [
                "Isolate the variable x",
                "What operation undoes the one in the equation?",
                "Check your answer by substituting back",
            ],
            "explanation": "To solve for x, we isolate it on one side of the equation.",
        }

    def _generate_default(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Default problem generator."""
        return self._generate_addition(difficulty)

    def check_solution(
        self,
        problem_id: str,
        student_answer: str,
        show_steps: bool = False,
    ) -> Dict[str, Any]:
        """Check student's solution."""
        # In production, fetch problem from database
        # For demo, we'll validate format

        # Clean answer
        student_answer = str(student_answer).strip()

        # Simple validation
        is_correct = bool(re.match(r"^-?\d+(/\d+)?$", student_answer))

        feedback = {
            "correct": is_correct,
            "feedback": (
                "Great job! That's correct!"
                if is_correct
                else "Not quite. Try again! You can do it!"
            ),
        }

        if show_steps and not is_correct:
            feedback["hint"] = "Remember to check your work step by step"
            feedback["next_step"] = "Try breaking down the problem into smaller parts"

        return feedback

    def generate_practice_set(
        self,
        topic: MathTopic,
        num_problems: int = 5,
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
    ) -> List[Problem]:
        """Generate a practice problem set."""
        problems = []

        for _ in range(num_problems):
            problem_data = self.generators.get(topic, self._generate_default)(difficulty)
            problem = Problem(
                id=f"practice_{topic.value}_{random.randint(1000, 9999)}",
                topic=topic,
                grade_level=GradeLevel.GRADE_5,  # Default
                difficulty=difficulty,
                **problem_data,
            )
            problems.append(problem)

        return problems
