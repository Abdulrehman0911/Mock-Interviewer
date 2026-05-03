# Model Training Flow — Zero-Cost Local Training

**Goal:** Train a regression model locally using 100 synthetically generated answers with rule-based labels. No APIs, no costs.

---

## Phase 1: Generate 100 Synthetic Interview Answers

### Step 1.1: Define Answer Templates

Create answer templates for different quality levels and question types.

**High Quality Answers (33 examples):**
- 200-300 words
- Clear structure (introduction, details, conclusion)
- Confident tone
- Specific examples
- No filler words
- Natural pausing

**Medium Quality Answers (33 examples):**
- 120-180 words
- Some structure but less organized
- Okay tone but some hesitation indicators
- Some specific examples
- Few filler words ("um", "like")
- Some natural pauses

**Low Quality Answers (34 examples):**
- 60-100 words
- Vague, rambling
- Uncertain tone
- Generic examples
- Many filler words ("um", "uh", "like", "you know", "basically")
- Awkward long pauses in text

### Step 1.2: Manually Write 100 Answers OR Use AI to Generate Them

**Method A (Fastest):** Use free ChatGPT/Claude to generate answers

Go to Claude free chat or ChatGPT free and ask:
```
Generate 35 high-quality interview answers for behavioral questions 
like "Tell me about a time you led a team" in 200-300 words each. 
Make them sound natural and confident. List them numbered 1-35.
```

Then ask for medium and low quality versions separately.

**Save all 100 answers in a file:** `raw_answers.json`

```json
[
  {
    "id": 1,
    "quality": "high",
    "question_type": "behavioral",
    "answer_text": "When I was leading the project management initiative at my previous company..."
  },
  {
    "id": 2,
    "quality": "medium",
    "question_type": "behavioral",
    "answer_text": "um, so like I had to manage this project once and it was pretty challenging..."
  }
]
```

---

## Phase 2: Simulate Realistic Features for Each Answer

### Step 2.1: Feature Simulation Rules

For each answer, assign features based on quality level. Use **realistic ranges**.

```python
FEATURE_RANGES = {
    "high": {
        "wpm": (135, 155),              # 135-155 words per minute
        "pause_count": (2, 4),          # 2-4 pauses in 60 seconds
        "pause_avg_duration": (0.5, 1.0),  # 0.5-1 second each
        "filler_count": (0, 2),         # 0-2 filler words
        "eye_contact_pct": (75, 90),    # 75-90% eye contact
        "head_pose_score": (8, 10),     # 8-10 out of 10
        "posture_score": (7, 10),       # 7-10 out of 10
        "facial_stability_score": (8, 10)  # 8-10 (composed)
    },
    "medium": {
        "wpm": (120, 180),
        "pause_count": (4, 8),
        "pause_avg_duration": (1.0, 2.0),
        "filler_count": (2, 8),
        "eye_contact_pct": (50, 75),
        "head_pose_score": (5, 8),
        "posture_score": (5, 8),
        "facial_stability_score": (5, 8)
    },
    "low": {
        "wpm": (75, 130) or (180, 220),  # Too slow OR too fast
        "pause_count": (8, 15),
        "pause_avg_duration": (2.0, 4.0),
        "filler_count": (8, 25),
        "eye_contact_pct": (15, 50),
        "head_pose_score": (2, 5),
        "posture_score": (2, 5),
        "facial_stability_score": (2, 5)
    }
}
```

### Step 2.2: Generate Simulated Features

Create `simulate_features.py`:

```python
import json
import random
import csv

# Load raw answers
with open('raw_answers.json', 'r') as f:
    answers = json.load(f)

feature_ranges = {
    "high": {
        "wpm": (135, 155),
        "pause_count": (2, 4),
        "pause_avg_duration": (0.5, 1.0),
        "filler_count": (0, 2),
        "eye_contact_pct": (75, 90),
        "head_pose_score": (8, 10),
        "posture_score": (7, 10),
        "facial_stability_score": (8, 10)
    },
    "medium": {
        "wpm": (120, 180),
        "pause_count": (4, 8),
        "pause_avg_duration": (1.0, 2.0),
        "filler_count": (2, 8),
        "eye_contact_pct": (50, 75),
        "head_pose_score": (5, 8),
        "posture_score": (5, 8),
        "facial_stability_score": (5, 8)
    },
    "low": {
        "wpm": list(range(75, 130)) + list(range(180, 220)),
        "pause_count": (8, 15),
        "pause_avg_duration": (2.0, 4.0),
        "filler_count": (8, 25),
        "eye_contact_pct": (15, 50),
        "head_pose_score": (2, 5),
        "posture_score": (2, 5),
        "facial_stability_score": (2, 5)
    }
}

# Generate features for each answer
features_list = []

for answer in answers:
    quality = answer['quality']
    ranges = feature_ranges[quality]
    
    # Generate random features within range
    features = {
        'answer_id': answer['id'],
        'transcript': answer['answer_text'],
        'transcript_length': len(answer['answer_text'].split()),
        'wpm': random.uniform(ranges['wpm'][0], ranges['wpm'][1]),
        'pause_count': random.randint(ranges['pause_count'][0], ranges['pause_count'][1]),
        'pause_avg_duration': random.uniform(ranges['pause_avg_duration'][0], ranges['pause_avg_duration'][1]),
        'filler_count': random.randint(ranges['filler_count'][0], ranges['filler_count'][1]),
        'eye_contact_pct': random.uniform(ranges['eye_contact_pct'][0], ranges['eye_contact_pct'][1]),
        'head_pose_score': random.randint(ranges['head_pose_score'][0], ranges['head_pose_score'][1]),
        'posture_score': random.randint(ranges['posture_score'][0], ranges['posture_score'][1]),
        'facial_stability_score': random.randint(ranges['facial_stability_score'][0], ranges['facial_stability_score'][1]),
        'question_difficulty': random.randint(1, 3),  # 1=easy, 2=medium, 3=hard
        'quality_level': quality
    }
    
    features_list.append(features)

# Save to CSV
with open('simulated_features.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=features_list[0].keys())
    writer.writeheader()
    writer.writerows(features_list)

print(f"✓ Generated features for {len(features_list)} answers")
print(f"✓ Saved to: simulated_features.csv")
```

**Run this script:**
```bash
python simulate_features.py
```

**Output:** `simulated_features.csv` with 100 rows, each with 11 feature columns + transcript

---

## Phase 3: Label Data with Rule-Based Scoring

### Step 3.1: Define Scoring Rules

Score each answer based on features (NO API CALLS):

```
Score = (eye_contact_score × 0.35) + 
        (wpm_score × 0.25) + 
        (filler_score × 0.15) + 
        (pause_score × 0.15) + 
        (posture_score × 0.10)

Where:
  eye_contact_score = (eye_contact_pct / 100) × 10
  wpm_score = 10 - abs(wpm - 145) / 15  (optimal WPM is 145)
  filler_score = 10 - min(filler_count, 10)  (fewer fillers = better)
  pause_score = 10 - (pause_count × 0.5)  (fewer long pauses = better)
  posture_score = (posture_score from features) / 10
```

### Step 3.2: Generate Labels

Create `label_data.py`:

```python
import pandas as pd
import numpy as np

# Load simulated features
df = pd.read_csv('simulated_features.csv')

def calculate_score(row):
    """Calculate score based on features"""
    
    # Eye contact contribution (0-10)
    eye_contact_score = (row['eye_contact_pct'] / 100) * 10
    
    # WPM contribution (optimal: 145 WPM)
    wpm_diff = abs(row['wpm'] - 145)
    wpm_score = max(0, 10 - (wpm_diff / 15))
    
    # Filler words contribution (fewer = better)
    filler_score = max(0, 10 - min(row['filler_count'], 10))
    
    # Pause contribution (fewer = better)
    pause_score = max(0, 10 - (row['pause_count'] * 0.5))
    
    # Posture contribution
    posture_score = (row['posture_score'] / 10) * 10
    
    # Weighted average
    final_score = (eye_contact_score * 0.35 + 
                   wpm_score * 0.25 + 
                   filler_score * 0.15 + 
                   pause_score * 0.15 + 
                   posture_score * 0.10)
    
    return round(np.clip(final_score, 1.0, 10.0), 1)

# Add score column
df['score'] = df.apply(calculate_score, axis=1)

# Save labeled dataset
df.to_csv('training_data.csv', index=False)

print(f"✓ Labeled {len(df)} answers")
print(f"✓ Score distribution:")
print(df['score'].describe())
print(f"✓ Saved to: training_data.csv")
```

**Run this script:**
```bash
python label_data.py
```

**Output:** `training_data.csv` with 100 rows, 12 columns (10 features + transcript + score)

---

## Phase 4: Train the Model

### Step 4.1: Load Data & Prepare

Create `train_model.py`:

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle

# Load labeled data
df = pd.read_csv('training_data.csv')

print(f"Dataset loaded: {df.shape[0]} samples")
print(f"\nScore distribution:")
print(df['score'].describe())

# Define features (exclude transcript and score)
feature_columns = [
    'transcript_length', 'wpm', 'pause_count', 'pause_avg_duration',
    'filler_count', 'eye_contact_pct', 'head_pose_score', 'posture_score',
    'facial_stability_score', 'question_difficulty'
]

X = df[feature_columns]
y = df['score']

print(f"\nFeatures: {feature_columns}")
print(f"Target: score (range {y.min():.1f} to {y.max():.1f})")
```

### Step 4.2: Split Data

```python
# 80-20 split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nTrain set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")
```

### Step 4.3: Train Three Models

```python
# Model 1: Linear Regression (baseline)
print("\n" + "="*50)
print("MODEL 1: Linear Regression")
print("="*50)

lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)
lr_pred = lr_model.predict(X_test_scaled)
lr_mae = mean_absolute_error(y_test, lr_pred)
lr_r2 = r2_score(y_test, lr_pred)

print(f"MAE: {lr_mae:.3f}")
print(f"R²: {lr_r2:.3f}")

# Model 2: Random Forest (recommended)
print("\n" + "="*50)
print("MODEL 2: Random Forest")
print("="*50)

rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
rf_model.fit(X_train_scaled, y_train)
rf_pred = rf_model.predict(X_test_scaled)
rf_mae = mean_absolute_error(y_test, rf_pred)
rf_r2 = r2_score(y_test, rf_pred)

print(f"MAE: {rf_mae:.3f}")
print(f"R²: {rf_r2:.3f}")

# Model 3: Neural Network
print("\n" + "="*50)
print("MODEL 3: Neural Network")
print("="*50)

nn_model = MLPRegressor(
    hidden_layer_sizes=(32, 16),
    max_iter=500,
    random_state=42
)
nn_model.fit(X_train_scaled, y_train)
nn_pred = nn_model.predict(X_test_scaled)
nn_mae = mean_absolute_error(y_test, nn_pred)
nn_r2 = r2_score(y_test, nn_pred)

print(f"MAE: {nn_mae:.3f}")
print(f"R²: {nn_r2:.3f}")
```

### Step 4.4: Pick Best Model & Save

```python
# Compare models
print("\n" + "="*50)
print("COMPARISON")
print("="*50)

models = {
    'Linear Regression': (lr_model, lr_mae, lr_r2),
    'Random Forest': (rf_model, rf_mae, rf_r2),
    'Neural Network': (nn_model, nn_mae, nn_r2)
}

best_model_name = min(models, key=lambda x: models[x][1])
best_model, best_mae, best_r2 = models[best_model_name]

print(f"\n✓ Best Model: {best_model_name}")
print(f"✓ MAE: {best_mae:.3f}")
print(f"✓ R²: {best_r2:.3f}")

# Save the best model
with open('scoring_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

# Save the scaler (IMPORTANT for inference)
with open('feature_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print(f"\n✓ Model saved: scoring_model.pkl")
print(f"✓ Scaler saved: feature_scaler.pkl")
```

**Run the complete training script:**
```bash
python train_model.py
```

**Output:**
- `scoring_model.pkl` — your trained model
- `feature_scaler.pkl` — the scaler for feature normalization
- Console output showing model comparison

---

## Phase 5: Test Your Model

### Step 5.1: Create Inference Function

Create `test_model.py`:

```python
import pickle
import numpy as np

# Load model and scaler
with open('scoring_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('feature_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

def predict_score(features_dict):
    """
    Predict score for a given set of features.
    
    features_dict should have:
    - transcript_length: int
    - wpm: float
    - pause_count: int
    - pause_avg_duration: float
    - filler_count: int
    - eye_contact_pct: float
    - head_pose_score: int (0-10)
    - posture_score: int (0-10)
    - facial_stability_score: int (0-10)
    - question_difficulty: int (1-3)
    """
    
    feature_order = [
        'transcript_length', 'wpm', 'pause_count', 'pause_avg_duration',
        'filler_count', 'eye_contact_pct', 'head_pose_score', 'posture_score',
        'facial_stability_score', 'question_difficulty'
    ]
    
    # Extract features in correct order
    X = np.array([[features_dict[feat] for feat in feature_order]])
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Predict
    score = model.predict(X_scaled)[0]
    
    # Ensure score is between 1-10
    score = np.clip(score, 1.0, 10.0)
    
    return round(score, 1)

# Test on sample data
test_features = {
    'transcript_length': 250,
    'wpm': 145,
    'pause_count': 3,
    'pause_avg_duration': 0.8,
    'filler_count': 1,
    'eye_contact_pct': 80,
    'head_pose_score': 8,
    'posture_score': 8,
    'facial_stability_score': 8,
    'question_difficulty': 2
}

predicted_score = predict_score(test_features)
print(f"Predicted score for high-quality answer: {predicted_score}/10")

# Test on low-quality answer
test_features_low = {
    'transcript_length': 80,
    'wpm': 100,
    'pause_count': 10,
    'pause_avg_duration': 3.0,
    'filler_count': 15,
    'eye_contact_pct': 25,
    'head_pose_score': 3,
    'posture_score': 3,
    'facial_stability_score': 3,
    'question_difficulty': 2
}

predicted_score_low = predict_score(test_features_low)
print(f"Predicted score for low-quality answer: {predicted_score_low}/10")
```

**Run test:**
```bash
python test_model.py
```

**Expected output:**
```
Predicted score for high-quality answer: 8.5/10
Predicted score for low-quality answer: 3.2/10
```

---

## Summary

| Phase | What | Output | Cost |
|---|---|---|---|
| 1 | Generate 100 answers | raw_answers.json | $0 |
| 2 | Simulate features | simulated_features.csv | $0 |
| 3 | Label with rules | training_data.csv | $0 |
| 4 | Train model | scoring_model.pkl + scaler | $0 |
| 5 | Test model | Working predictions | $0 |

**Total time:** 2-3 hours
**Total cost:** $0
**Model ready for:** Flask integration

