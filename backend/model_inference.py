"""Load and use the trained model for scoring answers."""

import pickle
import numpy as np
from pathlib import Path


class ModelInference:
    """Handles model and scaler loading, and prediction."""

    def __init__(self):
        """Initialize by loading model and scaler from disk."""
        self.model = None
        self.scaler = None
        self.model_path = Path(__file__).parent / "ml" / "answer_scoring_model.pkl"
        self.scaler_path = Path(__file__).parent / "ml" / "feature_scaler.pkl"
        
        self._load_artifacts()

    def _load_artifacts(self):
        """Load the trained model and scaler."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        if not self.scaler_path.exists():
            raise FileNotFoundError(f"Scaler not found at {self.scaler_path}")
        
        try:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            print("[OK] Model and scaler loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load model artifacts: {str(e)}")

    def predict_score(self, features_dict):
        """
        Predict an answer quality score using the trained model.

        Args:
            features_dict (dict): Dictionary with 10 required features:
                - transcript_length (int)
                - wpm (float)
                - pause_count (int)
                - pause_avg_duration (float)
                - filler_count (int)
                - eye_contact_pct (float)
                - head_pose_score (int)
                - posture_score (int)
                - facial_stability_score (int)
                - question_difficulty (int)

        Returns:
            float: Predicted score between 1.0 and 10.0, rounded to 1 decimal place.

        Raises:
            ValueError: If required features are missing or invalid.
            RuntimeError: If prediction fails.
        """
        required_features = [
            "transcript_length",
            "wpm",
            "pause_count",
            "pause_avg_duration",
            "filler_count",
            "eye_contact_pct",
            "head_pose_score",
            "posture_score",
            "facial_stability_score",
            "question_difficulty",
        ]

        # Validate all features are present
        missing = [f for f in required_features if f not in features_dict]
        if missing:
            raise ValueError(f"Missing required features: {', '.join(missing)}")

        try:
            # Extract features in correct order
            feature_values = np.array(
                [[float(features_dict[feat]) for feat in required_features]]
            )

            # Scale features using the fitted scaler
            scaled_features = self.scaler.transform(feature_values)

            # Make prediction
            prediction = float(self.model.predict(scaled_features)[0])

            # Clip to 1.0-10.0 range and round to 1 decimal
            score = np.clip(prediction, 1.0, 10.0)
            return round(score, 1)

        except Exception as e:
            raise RuntimeError(f"Prediction failed: {str(e)}")


# Global instance - load on module import
try:
    inference = ModelInference()
except Exception as e:
    print(f"[WARN] Failed to load model: {str(e)}")
    inference = None


def predict_score(features_dict):
    """
    Convenience function to predict score using global inference instance.

    Args:
        features_dict (dict): Dictionary with required features.

    Returns:
        float: Predicted score (1.0-10.0).

    Raises:
        RuntimeError: If model not loaded.
        ValueError: If features invalid.
    """
    if inference is None:
        raise RuntimeError("Model not loaded")
    return inference.predict_score(features_dict)
