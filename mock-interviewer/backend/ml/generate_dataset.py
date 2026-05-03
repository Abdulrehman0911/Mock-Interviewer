"""Generate a synthetic training dataset from interview Q&A answers.

This script extracts every answer from the source JSON, saves the extracted
answers to a temporary JSON file, simulates interview-performance features,
and writes the final dataset to `dataset.csv`.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
SOURCE_CANDIDATES = [
	DATA_DIR / "questionsAnswers.json",
	DATA_DIR / "AI_Engineering_Interview_Answers.json",
]
RAW_ANSWERS_PATH = BASE_DIR / "raw_answers.json"
DATASET_PATH = BASE_DIR / "dataset.csv"

CSV_COLUMNS = [
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
	"score",
]


def load_source_file() -> tuple[Path, Dict[str, Any]]:
	"""Load the first available interview JSON source file."""

	for candidate in SOURCE_CANDIDATES:
		if candidate.exists():
			with candidate.open("r", encoding="utf-8") as handle:
				data = json.load(handle)
			if not isinstance(data, dict):
				raise ValueError(f"Expected a JSON object at {candidate}")
			return candidate, data

	searched = ", ".join(str(path) for path in SOURCE_CANDIDATES)
	raise FileNotFoundError(f"No source JSON file found. Looked for: {searched}")


def difficulty_to_numeric(difficulty: str | None) -> int:
	"""Map a question difficulty label to a numeric feature value."""

	normalized = (difficulty or "").strip().lower()
	if normalized in {"easy", "simple", "basic"}:
		return 1
	if normalized in {"normal", "medium", "intermediate"}:
		return 2
	if normalized in {"hard", "difficult", "advanced"}:
		return 3
	return 2


def clamp_int(value: float, minimum: int, maximum: int) -> int:
	"""Clamp and round a numeric value to an integer range."""

	return int(max(minimum, min(maximum, round(value))))


def clamp_float(value: float, minimum: float, maximum: float) -> float:
	"""Clamp a float to the requested range."""

	return round(max(minimum, min(maximum, value)), 2)


def band_ratio(score: int, lower: int, upper: int) -> float:
	"""Normalize a score to a 0-1 value inside its quality band."""

	if upper <= lower:
		return 0.0
	return max(0.0, min(1.0, (score - lower) / float(upper - lower)))


def simulate_features(score: int, transcript_length: int, difficulty: str, rng: random.Random) -> Dict[str, float | int]:
	"""Create realistic interview-performance features for one answer."""

	if score >= 8:
		ratio = band_ratio(score, 8, 10)
		return {
			"transcript_length": transcript_length,
			"wpm": clamp_float(130 + ratio * 25 + rng.uniform(-3, 3), 130, 155),
			"pause_count": clamp_int(4 - ratio * 2 + rng.uniform(-0.4, 0.4), 2, 4),
			"pause_avg_duration": clamp_float(1.0 - ratio * 0.5 + rng.uniform(-0.08, 0.08), 0.5, 1.0),
			"filler_count": clamp_int(2 - ratio * 2 + rng.uniform(-0.4, 0.4), 0, 2),
			"eye_contact_pct": clamp_float(75 + ratio * 15 + rng.uniform(-2, 2), 75, 90),
			"head_pose_score": clamp_int(8 + ratio * 2 + rng.uniform(-0.3, 0.3), 8, 10),
			"posture_score": clamp_int(7 + ratio * 3 + rng.uniform(-0.3, 0.3), 7, 10),
			"facial_stability_score": clamp_int(8 + ratio * 2 + rng.uniform(-0.3, 0.3), 8, 10),
			"question_difficulty": difficulty_to_numeric(difficulty),
		}

	if score >= 5:
		ratio = band_ratio(score, 5, 7)
		return {
			"transcript_length": transcript_length,
			"wpm": clamp_float(100 + ratio * 30 + rng.uniform(-4, 4), 100, 130),
			"pause_count": clamp_int(8 - ratio * 4 + rng.uniform(-0.5, 0.5), 4, 8),
			"pause_avg_duration": clamp_float(2.0 - ratio * 1.0 + rng.uniform(-0.12, 0.12), 1.0, 2.0),
			"filler_count": clamp_int(8 - ratio * 6 + rng.uniform(-0.7, 0.7), 2, 8),
			"eye_contact_pct": clamp_float(50 + ratio * 25 + rng.uniform(-3, 3), 50, 75),
			"head_pose_score": clamp_int(5 + ratio * 3 + rng.uniform(-0.4, 0.4), 5, 8),
			"posture_score": clamp_int(5 + ratio * 3 + rng.uniform(-0.4, 0.4), 5, 8),
			"facial_stability_score": clamp_int(5 + ratio * 3 + rng.uniform(-0.4, 0.4), 5, 8),
			"question_difficulty": difficulty_to_numeric(difficulty),
		}

	ratio = band_ratio(score, 1, 4)
	return {
		"transcript_length": transcript_length,
		"wpm": clamp_float(75 + ratio * 25 + rng.uniform(-4, 4), 75, 100),
		"pause_count": clamp_int(15 - ratio * 7 + rng.uniform(-0.8, 0.8), 8, 15),
		"pause_avg_duration": clamp_float(4.0 - ratio * 2.0 + rng.uniform(-0.2, 0.2), 2.0, 4.0),
		"filler_count": clamp_int(25 - ratio * 17 + rng.uniform(-1.0, 1.0), 8, 25),
		"eye_contact_pct": clamp_float(15 + ratio * 35 + rng.uniform(-4, 4), 15, 50),
		"head_pose_score": clamp_int(2 + ratio * 3 + rng.uniform(-0.4, 0.4), 2, 5),
		"posture_score": clamp_int(2 + ratio * 3 + rng.uniform(-0.4, 0.4), 2, 5),
		"facial_stability_score": clamp_int(2 + ratio * 3 + rng.uniform(-0.4, 0.4), 2, 5),
		"question_difficulty": difficulty_to_numeric(difficulty),
	}


def extract_answers(source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
	"""Flatten the nested JSON structure into answer-level records."""

	answers: List[Dict[str, Any]] = []
	for role_name, questions in source_data.items():
		if not isinstance(questions, list):
			continue
		for question in questions:
			if not isinstance(question, dict):
				continue
			question_id = question.get("question_id")
			question_text = question.get("question", "")
			difficulty = question.get("difficulty", "medium")
			for answer in question.get("answers", []):
				if not isinstance(answer, dict):
					continue
				text = str(answer.get("text", "")).strip()
				quality_score = int(answer.get("quality_score", 0))
				if not text or quality_score < 1:
					continue
				answers.append(
					{
						"role": role_name,
						"question_id": question_id,
						"question": question_text,
						"difficulty": difficulty,
						"answer_text": text,
						"quality_score": quality_score,
						"reason": answer.get("reason", ""),
					}
				)
	return answers


def main() -> None:
	"""Generate the dataset and persist the extracted answer records."""

	source_path, source_data = load_source_file()
	answers = extract_answers(source_data)
	if not answers:
		raise ValueError(f"No answers were extracted from {source_path}")

	rng = random.Random(42)
	rows: List[Dict[str, Any]] = []

	for answer in answers:
		transcript_length = len(answer["answer_text"].split())
		features = simulate_features(
			score=answer["quality_score"],
			transcript_length=transcript_length,
			difficulty=str(answer.get("difficulty", "medium")),
			rng=rng,
		)
		rows.append({**features, "score": answer["quality_score"]})

	with RAW_ANSWERS_PATH.open("w", encoding="utf-8") as handle:
		json.dump(answers, handle, indent=2, ensure_ascii=False)

	with DATASET_PATH.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
		writer.writeheader()
		writer.writerows(rows)

	print(f"✓ Dataset generated: {len(rows)} samples in {DATASET_PATH.name}")
	print(f"✓ Extracted answers saved: {RAW_ANSWERS_PATH.name}")
	print(f"✓ Source JSON used: {source_path.name}")


if __name__ == "__main__":
	main()
