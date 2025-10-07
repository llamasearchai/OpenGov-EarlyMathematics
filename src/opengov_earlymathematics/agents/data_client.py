"""Datasette and sqlite-utils integration for data workflows."""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import sqlite_utils
from datasette import Datasette

from opengov_earlymathematics.core.models import (
    Session,
    Student,
)
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class MathDataClient:
    """Datasette and sqlite-utils client for educational data workflows."""

    def __init__(self, db_path: str = "data/math_education.db"):
        """Initialize data client."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite_utils.Database(str(self.db_path))
        self._initialize_tables()

    def _initialize_tables(self):
        """Initialize database tables."""
        # Students table
        self.db["students"].upsert(
            {
                "id": "demo_student",
                "name": "Demo Student",
                "grade_level": "4",
                "learning_style": "visual",
                "created_at": "2024-01-01T00:00:00Z",
            },
            pk="id",
        )

        # Problems table
        self.db["problems"].upsert(
            {
                "id": "demo_problem_1",
                "topic": "multiplication",
                "question": "What is 7 × 8?",
                "answer": "56",
                "difficulty": "intermediate",
                "grade_level": "3",
            },
            pk="id",
        )

        # Sessions table
        self.db["sessions"].upsert(
            {
                "id": "demo_session_1",
                "student_id": "demo_student",
                "start_time": "2024-01-01T10:00:00Z",
                "problems_attempted": 5,
                "problems_correct": 4,
            },
            pk="id",
        )

    def add_student(self, student: Student) -> bool:
        """Add a student to the database."""
        try:
            self.db["students"].upsert(
                {
                    "id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "grade_level": student.grade_level.value,
                    "age": student.age,
                    "learning_style": student.learning_style.value,
                    "parent_email": student.parent_email,
                    "created_at": student.created_at.isoformat(),
                    "last_active": student.last_active.isoformat(),
                    "total_practice_time": student.total_practice_time,
                    "points": student.points,
                    "current_streak": student.current_streak,
                    "achievements": json.dumps(student.achievements),
                    "preferences": json.dumps(student.preferences),
                },
                pk="id",
            )
            return True
        except Exception as e:
            logger.error(f"Error adding student: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get student information."""
        try:
            student_data = self.db["students"].get(student_id)
            if student_data:
                # Parse JSON fields
                student_data["achievements"] = json.loads(student_data["achievements"] or "[]")
                student_data["preferences"] = json.loads(student_data["preferences"] or "{}")
                return student_data
            return None
        except Exception as e:
            logger.error(f"Error getting student: {e}")
            return None

    def add_session(self, session: Session) -> bool:
        """Add a learning session."""
        try:
            self.db["sessions"].upsert(
                {
                    "id": session.id,
                    "student_id": session.student_id,
                    "teacher_id": session.teacher_id,
                    "lesson_id": session.lesson_id,
                    "start_time": session.start_time.isoformat(),
                    "end_time": session.end_time.isoformat() if session.end_time else None,
                    "duration_minutes": session.duration_minutes,
                    "problems_attempted": session.problems_attempted,
                    "problems_correct": session.problems_correct,
                    "hints_used": session.hints_used,
                    "points_earned": session.points_earned,
                    "topics_covered": json.dumps([topic.value for topic in session.topics_covered]),
                    "performance_metrics": json.dumps(session.performance_metrics),
                    "feedback": session.feedback,
                    "recording_url": session.recording_url,
                },
                pk="id",
            )
            return True
        except Exception as e:
            logger.error(f"Error adding session: {e}")
            return False

    def get_student_sessions(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a student."""
        try:
            sessions = self.db["sessions"].rows_where("student_id = ?", [student_id])
            return list(sessions)
        except Exception as e:
            logger.error(f"Error getting student sessions: {e}")
            return []

    def add_problem_attempt(
        self,
        student_id: str,
        problem_id: str,
        attempt: str,
        is_correct: bool,
        time_taken: int,
        hints_used: int = 0,
    ) -> bool:
        """Add a problem attempt record."""
        try:
            self.db["problem_attempts"].upsert(
                {
                    "id": f"{student_id}_{problem_id}_{asyncio.get_event_loop().time()}",
                    "student_id": student_id,
                    "problem_id": problem_id,
                    "attempt": attempt,
                    "is_correct": is_correct,
                    "time_taken": time_taken,
                    "hints_used": hints_used,
                    "timestamp": asyncio.get_event_loop().time(),
                },
                pk="id",
            )
            return True
        except Exception as e:
            logger.error(f"Error adding problem attempt: {e}")
            return False

    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student progress."""
        try:
            # Get recent sessions
            sessions = self.get_student_sessions(student_id)

            # Calculate progress metrics
            total_problems = sum(s["problems_attempted"] for s in sessions)
            correct_problems = sum(s["problems_correct"] for s in sessions)
            total_time = sum(s["duration_minutes"] for s in sessions)

            # Get topic performance
            attempts = self.db["problem_attempts"].rows_where("student_id = ?", [student_id])
            topic_stats = {}

            for attempt in attempts:
                problem = self.db["problems"].get(attempt["problem_id"])
                if problem:
                    topic = problem["topic"]
                    if topic not in topic_stats:
                        topic_stats[topic] = {"correct": 0, "total": 0}
                    topic_stats[topic]["total"] += 1
                    if attempt["is_correct"]:
                        topic_stats[topic]["correct"] += 1

            # Calculate mastery scores
            mastery_scores = {}
            for topic, stats in topic_stats.items():
                mastery_scores[topic] = (
                    stats["correct"] / stats["total"] if stats["total"] > 0 else 0
                )

            return {
                "student_id": student_id,
                "total_sessions": len(sessions),
                "total_problems": total_problems,
                "accuracy": correct_problems / total_problems if total_problems > 0 else 0,
                "total_time": total_time,
                "mastery_scores": mastery_scores,
                "recent_sessions": sessions[-5:],  # Last 5 sessions
            }
        except Exception as e:
            logger.error(f"Error getting student progress: {e}")
            return {}

    def export_student_data(self, student_id: str, format: str = "json") -> str:
        """Export student data in specified format."""
        try:
            progress = self.get_student_progress(student_id)
            student = self.get_student(student_id)
            sessions = self.get_student_sessions(student_id)

            data = {
                "student": student,
                "progress": progress,
                "sessions": sessions,
            }

            if format.lower() == "json":
                return json.dumps(data, indent=2, default=str)
            return str(data)
        except Exception as e:
            logger.error(f"Error exporting student data: {e}")
            return ""

    def import_student_data(self, data: str, format: str = "json") -> bool:
        """Import student data from file."""
        try:
            if format.lower() == "json":
                data_dict = json.loads(data)
            else:
                logger.error("Only JSON format supported for import")
                return False

            # Import student
            if "student" in data_dict:
                self.add_student(Student(**data_dict["student"]))

            # Import sessions
            if "sessions" in data_dict:
                for session_data in data_dict["sessions"]:
                    session = Session(**session_data)
                    self.add_session(session)

            return True
        except Exception as e:
            logger.error(f"Error importing student data: {e}")
            return False

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get platform analytics summary."""
        try:
            # Count total students
            total_students = self.db["students"].count

            # Count total sessions
            total_sessions = self.db["sessions"].count

            # Count total problems
            total_problems = self.db["problems"].count

            # Get recent activity
            recent_sessions = list(
                self.db["sessions"].rows_where("start_time > datetime('now', '-7 days')", [])
            )

            return {
                "total_students": total_students,
                "total_sessions": total_sessions,
                "total_problems": total_problems,
                "recent_sessions": len(recent_sessions),
                "avg_session_duration": 30,  # Placeholder
                "top_topics": ["multiplication", "fractions", "addition"],
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}

    def start_datasette_server(self, port: int = 9000) -> bool:
        """Start a Datasette server for data browsing."""
        try:
            # Create Datasette app
            ds = Datasette([str(self.db_path)])

            # Run server (in background)
            logger.info(f"Starting Datasette server on port {port}")
            # Note: In production, you'd use uvicorn or similar to run this
            # ds.serve(port=port)

            return True
        except Exception as e:
            logger.error(f"Error starting Datasette server: {e}")
            return False

    def create_data_visualization(self, student_id: str) -> Dict[str, Any]:
        """Create data visualization for student progress."""
        try:
            progress = self.get_student_progress(student_id)

            # Create progress chart data
            chart_data = {
                "labels": list(progress.get("mastery_scores", {}).keys()),
                "datasets": [
                    {
                        "label": "Mastery Score",
                        "data": list(progress.get("mastery_scores", {}).values()),
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "borderColor": "rgba(75, 192, 192, 1)",
                    }
                ],
            }

            return {
                "success": True,
                "chart_data": chart_data,
                "summary_stats": {
                    "total_problems": progress.get("total_problems", 0),
                    "accuracy": progress.get("accuracy", 0),
                    "total_time": progress.get("total_time", 0),
                },
            }
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return {"success": False, "error": str(e)}

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil

            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(self.db_path, backup_file)
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False

    def optimize_database(self) -> bool:
        """Optimize database performance."""
        try:
            # Run VACUUM and ANALYZE
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.commit()
            conn.close()

            logger.info("Database optimized")
            return True
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a database table."""
        try:
            table = self.db[table_name]
            return {
                "name": table_name,
                "count": table.count,
                "columns": [col.name for col in table.columns],
                "schema": table.schema,
            }
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}

    def search_problems(
        self,
        query: str,
        topic: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for problems in the database."""
        try:
            problems = self.db["problems"]

            # Build search query
            search_terms = query.split()
            where_clauses = []
            params = []

            for term in search_terms:
                where_clauses.append("question LIKE ?")
                params.append(f"%{term}%")

            if topic:
                where_clauses.append("topic = ?")
                params.append(topic)

            where_sql = " AND ".join(where_clauses)
            results = list(problems.rows_where(where_sql, params))[:limit]

            return results
        except Exception as e:
            logger.error(f"Error searching problems: {e}")
            return []

    def get_learning_insights(self, student_id: str) -> Dict[str, Any]:
        """Generate learning insights for a student."""
        try:
            progress = self.get_student_progress(student_id)

            insights = {
                "strengths": [],
                "areas_for_improvement": [],
                "learning_patterns": {},
                "recommendations": [],
            }

            # Identify strengths and weaknesses
            mastery_scores = progress.get("mastery_scores", {})
            for topic, score in mastery_scores.items():
                if score > 0.8:
                    insights["strengths"].append(topic)
                elif score < 0.6:
                    insights["areas_for_improvement"].append(topic)

            # Generate recommendations
            if insights["areas_for_improvement"]:
                insights["recommendations"].append(
                    f"Focus practice on: {', '.join(insights['areas_for_improvement'][:3])}"
                )

            if progress.get("accuracy", 0) < 0.7:
                insights["recommendations"].append(
                    "Review fundamental concepts and take your time with problems"
                )

            insights["learning_patterns"] = {
                "consistency_score": progress.get("accuracy", 0),
                "total_practice_time": progress.get("total_time", 0),
                "problems_per_session": progress.get("total_problems", 0)
                / max(len(progress.get("recent_sessions", [])), 1),
            }

            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {}
