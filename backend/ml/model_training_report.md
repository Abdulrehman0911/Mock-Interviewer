# Mock Interviewer Model Training Report

- Generated: 2026-04-28 04:17:01
- Dataset samples: 275
- Train split: 220
- Test split: 55
- Target range: 1.0 to 10.0

## Model Comparison

| Model | MAE | MSE | R² |
| --- | ---: | ---: | ---: |
| Linear Regression | 0.134 | 0.036 | 0.997 |
| Random Forest Regressor | 0.022 | 0.011 | 0.999 |
| MLP Regressor | 0.179 | 0.056 | 0.995 |

## Best Model

- Selected model: Random Forest Regressor
- MAE: 0.022
- MSE: 0.011
- R²: 0.999
- Model artifact: answer_scoring_model.pkl
- Scaler artifact: feature_scaler.pkl

## Notes

- Features were standardized with `StandardScaler` before training.
- The model with the lowest MAE was saved for inference.

## Inference Sanity Checks

- Generated: 2026-04-28 04:23:12

| Scenario | Predicted score |
| --- | ---: |
| High quality answer | 9.0 |
| Medium quality answer | 6.3 |
| Low quality answer | 2.1 |
