"""Load the trained model and run inference examples."""

from __future__ import annotations

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "answer_scoring_model.pkl"
SCALER_PATH = BASE_DIR / "feature_scaler.pkl"
REPORT_PATH = BASE_DIR / "model_training_report.md"

FEATURE_ORDER = [
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


def load_artifacts() -> tuple[Any, Any]:
	"""Load the serialized regression model and the fitted scaler."""

	if not MODEL_PATH.exists():
		raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
	if not SCALER_PATH.exists():
		raise FileNotFoundError(f"Scaler file not found: {SCALER_PATH}")

	with MODEL_PATH.open("rb") as model_handle:
		model = pickle.load(model_handle)
	with SCALER_PATH.open("rb") as scaler_handle:
		scaler = pickle.load(scaler_handle)

	return model, scaler


def validate_features(features_dict: Dict[str, Any]) -> None:
	"""Ensure the input payload contains every required feature."""

	missing = [feature for feature in FEATURE_ORDER if feature not in features_dict]
	if missing:
		raise ValueError(f"Missing required features: {', '.join(missing)}")


def predict_score(features_dict: Dict[str, Any]) -> float:
	"""Predict a 1-10 answer quality score from interview features."""

	validate_features(features_dict)
	model, scaler = load_artifacts()

	feature_values = np.asarray(
		[[float(features_dict[name]) for name in FEATURE_ORDER]], dtype=float
	)
	scaled_features = scaler.transform(feature_values)
	prediction = float(model.predict(scaled_features)[0])
	return round(float(np.clip(prediction, 1.0, 10.0)), 1)


def append_report_section(results: List[Tuple[str, float]]) -> None:
	"""Append inference sanity checks to the markdown report."""

	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	lines = [
		"",
		"## Inference Sanity Checks",
		"",
		f"- Generated: {timestamp}",
		"",
		"| Scenario | Predicted score |",
		"| --- | ---: |",
	]

	for label, score in results:
		lines.append(f"| {label} | {score:.1f} |")

	existing = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.exists() else ""
	REPORT_PATH.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
	"""Run the three requested sample predictions and print the results."""

	scenarios = [
		(
			"High quality answer",
			{
				"transcript_length": 240,
				"wpm": 145,
				"pause_count": 3,
				"pause_avg_duration": 0.8,
				"filler_count": 1,
				"eye_contact_pct": 85,
				"head_pose_score": 9,
				"posture_score": 9,
				"facial_stability_score": 9,
				"question_difficulty": 2,
			},
		),
		(
			"Medium quality answer",
			{
				"transcript_length": 160,
				"wpm": 100,
				"pause_count": 6,
				"pause_avg_duration": 1.5,
				"filler_count": 5,
				"eye_contact_pct": 65,
				"head_pose_score": 6,
				"posture_score": 6,
				"facial_stability_score": 6,
				"question_difficulty": 2,
			},
		),
		(
			"Low quality answer",
			{
				"transcript_length": 85,
				"wpm": 70,
				"pause_count": 12,
				"pause_avg_duration": 3.0,
				"filler_count": 15,
				"eye_contact_pct": 25,
				"head_pose_score": 3,
				"posture_score": 3,
				"facial_stability_score": 3,
				"question_difficulty": 2,
			},
		),
	]

	results: List[Tuple[str, float]] = []
	for label, features in scenarios:
		score = predict_score(features)
		results.append((label, score))
		print(f"{label}: {score}/10")

	append_report_section(results)
	print(f"✓ Inference results appended to {REPORT_PATH.name}")


if __name__ == "__main__":
	main()
