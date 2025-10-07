"""Machine learning models for student assessment and personalization."""

from typing import Dict, List

import numpy as np

# Optional sklearn imports with graceful fallbacks for test environments
try:  # pragma: no cover - import guard
    from sklearn.cluster import KMeans  # type: ignore
    from sklearn.ensemble import RandomForestClassifier  # type: ignore
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.model_selection import train_test_split  # type: ignore
    from sklearn.preprocessing import StandardScaler  # type: ignore
except Exception:  # pragma: no cover - provide minimal fallbacks
    class _SimpleRF:
        def fit(self, X, y):
            # Store mean of y for a trivial probability predictor
            self._p = float(np.mean(y)) if len(y) else 0.5
            return self

        def predict_proba(self, X):
            # Return [P(0), P(1)] with a constant probability
            p1 = getattr(self, "_p", 0.5)
            p0 = 1.0 - p1
            return np.array([[p0, p1] for _ in range(len(X))])

    class _SimpleKMeans:
        def __init__(self, n_clusters=4, random_state=None):
            self.n_clusters = n_clusters

        def fit(self, X):
            # No-op fit
            self._fit = True
            return self

        def predict(self, X):
            # Deterministic, simple cluster assignment based on sum of features
            return np.array([int(sum(row)) % self.n_clusters for row in X])

    class _SimpleScaler:
        def fit_transform(self, X):
            X = np.asarray(X, dtype=float)
            self._mean = X.mean(axis=0)
            self._std = X.std(axis=0)
            self._std[self._std == 0] = 1.0
            return (X - self._mean) / self._std

        def transform(self, X):
            X = np.asarray(X, dtype=float)
            mean = getattr(self, "_mean", np.zeros(X.shape[1]))
            std = getattr(self, "_std", np.ones(X.shape[1]))
            std[std == 0] = 1.0
            return (X - mean) / std

    class _SimpleVectorizer:
        def __init__(self, max_features=1000):
            self.max_features = max_features

        def fit_transform(self, texts):  # not used in current code
            return np.zeros((len(texts), 1))

    def train_test_split(X, y, test_size=0.2, random_state=42):  # type: ignore
        # Simple split without shuffling for environments lacking sklearn
        n = len(X)
        cut = max(1, int(n * (1 - test_size)))
        return X[:cut], X[cut:], y[:cut], y[cut:]

    # Assign fallbacks
    RandomForestClassifier = _SimpleRF  # type: ignore
    KMeans = _SimpleKMeans  # type: ignore
    StandardScaler = _SimpleScaler  # type: ignore
    TfidfVectorizer = _SimpleVectorizer  # type: ignore

from opengov_earlymathematics.core.models import MathTopic, Student
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)


class StudentModel:
    """Machine learning model for student assessment and personalization."""

    def __init__(self):
        """Initialize student model."""
        self.performance_model = None
        self.cluster_model = None
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
        self.is_trained = False

    def train_model(self, training_data: List[Dict]) -> bool:
        """Train the student performance prediction model."""
        try:
            if len(training_data) < 10:
                logger.warning("Insufficient training data")
                return False

            # Extract features and labels
            features = []
            labels = []

            for record in training_data:
                feature_vector = self._extract_features(record)
                features.append(feature_vector)
                labels.append(record.get("performance", 0.5))

            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(labels)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train model
            self.performance_model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42
            )
            self.performance_model.fit(X_train_scaled, y_train)

            # Train clustering model for learning styles
            self.cluster_model = KMeans(n_clusters=4, random_state=42)
            self.cluster_model.fit(X_train_scaled)

            self.is_trained = True
            logger.info("Student model trained successfully")
            return True

        except Exception as e:
            logger.error(f"Error training student model: {e}")
            return False

    def _extract_features(self, record: Dict) -> List[float]:
        """Extract numerical features from student record."""
        features = []

        # Performance metrics
        features.append(record.get("avg_score", 0.5))
        features.append(record.get("completion_rate", 0.5))
        features.append(record.get("time_per_problem", 60.0))
        features.append(record.get("hint_usage_rate", 0.2))

        # Learning style indicators
        features.append(record.get("visual_score", 0.5))
        features.append(record.get("auditory_score", 0.5))
        features.append(record.get("kinesthetic_score", 0.5))

        # Engagement metrics
        features.append(record.get("session_frequency", 3.0))
        features.append(record.get("avg_session_length", 30.0))
        features.append(record.get("streak_length", 1.0))

        # Topic-specific performance
        topics = ["addition", "subtraction", "multiplication", "division", "fractions"]
        for topic in topics:
            features.append(record.get(f"{topic}_mastery", 0.5))

        return features

    def predict_performance(self, student: Student, topic: MathTopic, difficulty: str) -> float:
        """Predict student performance on a topic."""
        if not self.is_trained:
            return 0.5  # Default prediction

        try:
            # Create feature vector
            features = self._create_student_feature_vector(student, topic, difficulty)
            features_scaled = self.scaler.transform([features])

            # Make prediction
            prediction = self.performance_model.predict_proba(features_scaled)
            return float(prediction[0][1])  # Probability of success

        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return 0.5

    def _create_student_feature_vector(
        self, student: Student, topic: MathTopic, difficulty: str
    ) -> List[float]:
        """Create feature vector for a student-topic pair."""
        features = []

        # Student characteristics
        features.append(student.age / 18.0)  # Normalize age
        features.append(1.0 if student.learning_style.value == "visual" else 0.0)
        features.append(1.0 if student.learning_style.value == "auditory" else 0.0)
        features.append(1.0 if student.learning_style.value == "kinesthetic" else 0.0)

        # Grade level encoding
        grade_mapping = {
            "K": 0,
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "11": 11,
            "12": 12,
        }
        features.append(grade_mapping.get(student.grade_level.value, 6) / 12.0)

        # Difficulty encoding
        difficulty_scores = {"beginner": 0.2, "intermediate": 0.5, "advanced": 0.8, "expert": 1.0}
        features.append(difficulty_scores.get(difficulty, 0.5))

        # Historical performance (placeholder - would be fetched from DB)
        features.append(0.7)  # avg_score
        features.append(0.8)  # completion_rate
        features.append(45.0)  # time_per_problem
        features.append(0.15)  # hint_usage_rate

        # Topic encoding (simplified)
        topic_features = self._encode_topic(topic)
        features.extend(topic_features)

        return features

    def _encode_topic(self, topic: MathTopic) -> List[float]:
        """Encode topic as numerical features."""
        # Simple encoding based on topic category
        topic_categories = {
            "counting": [1, 0, 0, 0, 0],
            "addition": [0, 1, 0, 0, 0],
            "subtraction": [0, 1, 0, 0, 0],
            "multiplication": [0, 0, 1, 0, 0],
            "division": [0, 0, 1, 0, 0],
            "fractions": [0, 0, 0, 1, 0],
            "algebra": [0, 0, 0, 0, 1],
        }

        topic_str = topic.value.lower()
        for category, encoding in topic_categories.items():
            if category in topic_str:
                return encoding

        return [0, 0, 0, 0, 0]  # Default encoding

    def recommend_learning_style(self, student_data: Dict) -> str:
        """Recommend optimal learning style based on performance data."""
        if not self.is_trained:
            return "visual"  # Default

        try:
            features = self._extract_features(student_data)
            features_scaled = self.scaler.transform([features])

            cluster = self.cluster_model.predict(features_scaled)[0]

            # Map clusters to learning styles
            style_mapping = {0: "visual", 1: "auditory", 2: "kinesthetic", 3: "reading_writing"}

            return style_mapping.get(cluster, "visual")

        except Exception as e:
            logger.error(f"Error recommending learning style: {e}")
            return "visual"

    def identify_at_risk_students(self, student_data: List[Dict]) -> List[str]:
        """Identify students at risk of falling behind."""
        at_risk_students = []

        for student_record in student_data:
            risk_score = self._calculate_risk_score(student_record)

            if risk_score > 0.7:  # Threshold for at-risk
                at_risk_students.append(student_record.get("student_id"))

        return at_risk_students

    def _calculate_risk_score(self, student_record: Dict) -> float:
        """Calculate risk score for a student."""
        risk_factors = []

        # Low performance
        if student_record.get("avg_score", 1.0) < 0.6:
            risk_factors.append(1.0)

        # Low engagement
        if student_record.get("session_frequency", 7.0) < 2:
            risk_factors.append(1.0)

        # High hint usage
        if student_record.get("hint_usage_rate", 0.0) > 0.5:
            risk_factors.append(0.8)

        # Declining performance trend
        if student_record.get("performance_trend", 0.0) < -0.1:
            risk_factors.append(0.9)

        # Long time per problem
        if student_record.get("time_per_problem", 30.0) > 120:
            risk_factors.append(0.7)

        return min(sum(risk_factors) / len(risk_factors), 1.0) if risk_factors else 0.0

    def generate_insights(self, student: Student, performance_history: List[Dict]) -> Dict:
        """Generate insights about student learning patterns."""
        insights = {
            "strengths": [],
            "weaknesses": [],
            "learning_patterns": {},
            "recommendations": [],
        }

        if not performance_history:
            return insights

        # Analyze topic performance
        topic_performance = {}
        for record in performance_history:
            topic = record.get("topic")
            score = record.get("score", 0.5)

            if topic:
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(score)

        # Identify strengths and weaknesses
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)

            if avg_score > 0.8:
                insights["strengths"].append(topic)
            elif avg_score < 0.6:
                insights["weaknesses"].append(topic)

        # Learning patterns
        insights["learning_patterns"] = {
            "avg_session_length": sum(r.get("session_length", 30) for r in performance_history)
            / len(performance_history),
            "preferred_time": self._find_preferred_time(performance_history),
            "consistency_score": self._calculate_consistency(performance_history),
        }

        # Generate recommendations
        if len(insights["weaknesses"]) > 0:
            insights["recommendations"].append(
                f"Focus additional practice on: {', '.join(insights['weaknesses'][:3])}"
            )

        if insights["learning_patterns"]["consistency_score"] < 0.6:
            insights["recommendations"].append(
                "Establish a regular practice schedule for better progress"
            )

        return insights

    def _find_preferred_time(self, performance_history: List[Dict]) -> str:
        """Find student's preferred learning time."""
        # Placeholder implementation
        return "afternoon"

    def _calculate_consistency(self, performance_history: List[Dict]) -> float:
        """Calculate learning consistency score."""
        if len(performance_history) < 3:
            return 0.5

        scores = [r.get("score", 0.5) for r in performance_history]
        return 1.0 - (np.std(scores) / 0.5)  # Normalize by max possible std
