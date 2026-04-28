"""Load and manage interview questions from JSON."""

import json
import random
from pathlib import Path


class QuestionManager:
    """Manages loading and retrieving interview questions."""

    def __init__(self):
        """Initialize by loading questions from JSON file."""
        self.questions_data = None
        self.json_path = Path(__file__).parent / "data" / "questionsAnswers.json"
        self._load_questions()

    def _load_questions(self):
        """Load questions from JSON file."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"Questions file not found at {self.json_path}")

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.questions_data = json.load(f)
            print(f"✓ Loaded questions for {len(self.questions_data)} roles")
        except Exception as e:
            raise RuntimeError(f"Failed to load questions: {str(e)}")

    def get_all_roles(self):
        """
        Get all available job roles.

        Returns:
            list: List of role names (e.g., ["Software Engineer", "Data Scientist"]).
        """
        if self.questions_data is None:
            raise RuntimeError("Questions not loaded")
        return list(self.questions_data.keys())

    def get_questions_for_role(self, role):
        """
        Get all questions for a specific role.

        Args:
            role (str): Job role name (e.g., "Software Engineer").

        Returns:
            list: List of questions with keys: question_id, question, difficulty.

        Raises:
            ValueError: If role not found.
        """
        if role not in self.questions_data:
            available = ", ".join(self.get_all_roles())
            raise ValueError(
                f"Role '{role}' not found. Available roles: {available}"
            )

        questions = []
        for q in self.questions_data[role]:
            questions.append(
                {
                    "question_id": q.get("question_id"),
                    "question": q.get("question"),
                    "difficulty": q.get("difficulty"),
                }
            )
        return questions

    def get_random_questions(self, role, count=5):
        """
        Get N random questions for a specific role.

        Args:
            role (str): Job role name.
            count (int): Number of questions to return (default 5).

        Returns:
            list: List of random questions.

        Raises:
            ValueError: If role not found or count exceeds available questions.
        """
        questions = self.get_questions_for_role(role)

        if count > len(questions):
            raise ValueError(
                f"Requested {count} questions but only {len(questions)} available for {role}"
            )

        return random.sample(questions, count)


# Global instance
try:
    question_manager = QuestionManager()
except Exception as e:
    print(f"⚠ Warning: Failed to load questions: {str(e)}")
    question_manager = None


def get_all_roles():
    """Get all available roles."""
    if question_manager is None:
        raise RuntimeError("Question manager not initialized")
    return question_manager.get_all_roles()


def get_questions_for_role(role):
    """Get questions for a role."""
    if question_manager is None:
        raise RuntimeError("Question manager not initialized")
    return question_manager.get_questions_for_role(role)


def get_random_questions(role, count=5):
    """Get random questions for a role."""
    if question_manager is None:
        raise RuntimeError("Question manager not initialized")
    return question_manager.get_random_questions(role, count)
