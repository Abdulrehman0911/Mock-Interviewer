"""Train and compare regression models for interview answer scoring."""

from __future__ import annotations

import csv
import pickle
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "answer_scoring_model.pkl"
SCALER_PATH = BASE_DIR / "feature_scaler.pkl"
REPORT_PATH = BASE_DIR / "model_training_report.md"

FEATURE_COLUMNS = [
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


@dataclass
class ModelResult:
	"""Container for evaluation metrics and the fitted estimator."""

	name: str
	estimator: Any
	mae: float
	mse: float
	r2: float


def load_dataset(path: Path) -> Tuple[np.ndarray, np.ndarray]:
	"""Load the generated CSV dataset into feature and target arrays."""

	if not path.exists():
		raise FileNotFoundError(
			f"Dataset not found at {path}. Run generate_dataset.py first."
		)

	rows = []
	with path.open("r", encoding="utf-8") as handle:
		reader = csv.DictReader(handle)
		if reader.fieldnames is None:
			raise ValueError(f"Dataset CSV at {path} does not contain headers")
		for row in reader:
			rows.append(row)

	if not rows:
		raise ValueError(f"Dataset at {path} is empty")

	feature_rows = []
	target_rows = []
	for row in rows:
		try:
			feature_rows.append([float(row[column]) for column in FEATURE_COLUMNS])
			target_rows.append(float(row["score"]))
		except KeyError as exc:
			raise KeyError(f"Missing required column in dataset: {exc}") from exc
		except ValueError as exc:
			raise ValueError(f"Could not convert dataset row to numeric values: {row}") from exc

	return np.asarray(feature_rows, dtype=float), np.asarray(target_rows, dtype=float)


def format_metrics_table(results: List[ModelResult]) -> str:
	"""Build a markdown comparison table for the evaluated models."""

	lines = ["| Model | MAE | MSE | R² |", "| --- | ---: | ---: | ---: |"]
	for result in results:
		lines.append(
			f"| {result.name} | {result.mae:.3f} | {result.mse:.3f} | {result.r2:.3f} |"
		)
	return "\n".join(lines)


def write_report(
	*,
	source_samples: int,
	train_size: int,
	test_size: int,
	score_min: float,
	score_max: float,
	results: List[ModelResult],
	best_result: ModelResult,
) -> None:
	"""Persist a markdown report with the training run details."""

	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	lines = [
		"# Mock Interviewer Model Training Report",
		"",
		f"- Generated: {timestamp}",
		f"- Dataset samples: {source_samples}",
		f"- Train split: {train_size}",
		f"- Test split: {test_size}",
		f"- Target range: {score_min:.1f} to {score_max:.1f}",
		"",
		"## Model Comparison",
		"",
		format_metrics_table(results),
		"",
		"## Best Model",
		"",
		f"- Selected model: {best_result.name}",
		f"- MAE: {best_result.mae:.3f}",
		f"- MSE: {best_result.mse:.3f}",
		f"- R²: {best_result.r2:.3f}",
		f"- Model artifact: {MODEL_PATH.name}",
		f"- Scaler artifact: {SCALER_PATH.name}",
		"",
		"## Notes",
		"",
		"- Features were standardized with `StandardScaler` before training.",
		"- The model with the lowest MAE was saved for inference.",
	]

	REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fit_and_score_models(
	x_train: np.ndarray,
	x_test: np.ndarray,
	y_train: np.ndarray,
	y_test: np.ndarray,
) -> List[ModelResult]:
	"""Train each regression model and compute its evaluation metrics."""

	candidates: List[Tuple[str, Any]] = [
		("Linear Regression", LinearRegression()),
		(
			"Random Forest Regressor",
			RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
		),
		(
			"MLP Regressor",
			MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42),
		),
	]

	results: List[ModelResult] = []

	for name, estimator in candidates:
		estimator.fit(x_train, y_train)
		predictions = estimator.predict(x_test)
		results.append(
			ModelResult(
				name=name,
				estimator=estimator,
				mae=mean_absolute_error(y_test, predictions),
				mse=mean_squared_error(y_test, predictions),
				r2=r2_score(y_test, predictions),
			)
		)

	return results


def main() -> None:
	"""Train models, compare metrics, and save the best performer."""

	warnings.filterwarnings("ignore", category=ConvergenceWarning)

	x, y = load_dataset(DATASET_PATH)
	print(f"Dataset loaded: {len(x)} samples")

	x_train, x_test, y_train, y_test = train_test_split(
		x, y, test_size=0.2, random_state=42
	)

	scaler = StandardScaler()
	x_train_scaled = scaler.fit_transform(x_train)
	x_test_scaled = scaler.transform(x_test)

	print(f"Train set: {len(x_train_scaled)} samples")
	print(f"Test set: {len(x_test_scaled)} samples")

	results = fit_and_score_models(x_train_scaled, x_test_scaled, y_train, y_test)

	print("\nModel comparison")
	print("=" * 72)
	print(f"{'Model':<28} {'MAE':>10} {'MSE':>12} {'R²':>10}")
	print("-" * 72)
	for result in results:
		print(f"{result.name:<28} {result.mae:>10.3f} {result.mse:>12.3f} {result.r2:>10.3f}")

	best_result = min(results, key=lambda item: item.mae)

	with MODEL_PATH.open("wb") as model_handle:
		pickle.dump(best_result.estimator, model_handle)

	with SCALER_PATH.open("wb") as scaler_handle:
		pickle.dump(scaler, scaler_handle)

	print(
		f"\n✓ Best model saved: {best_result.name} with MAE={best_result.mae:.3f}"
	)
	print(f"✓ Model file: {MODEL_PATH.name}")
	print(f"✓ Scaler file: {SCALER_PATH.name}")

	write_report(
		source_samples=len(x),
		train_size=len(x_train_scaled),
		test_size=len(x_test_scaled),
		score_min=float(np.min(y)),
		score_max=float(np.max(y)),
		results=results,
		best_result=best_result,
	)
	print(f"✓ Training report written: {REPORT_PATH.name}")


if __name__ == "__main__":
	main()
