# Mock Interviewer — Complete Implementation Plan

> **Course:** Artificial Intelligence (Track A — Application Development)  
> **Team:** 4 members (roles TBD by team lead)  
> **Stack:** React + Firebase (Frontend) · Flask + Python (Backend) · Gemini API · Whisper API · MediaPipe  
> **Hosting:** Render (Backend) · Vercel (Frontend) · Firebase (Auth + DB + Storage)

---

## 1. Product Vision

A web-based AI Mock Interviewer that simulates real company interviews. The user creates an account, uploads their CV, selects a target company and role, and conducts a live video interview. The system analyzes both **what they say** (transcript quality, relevance, depth) and **how they say it** (eye contact, facial confidence, posture, speech pace). A detailed scored report is generated after each session.

---

## 2. Interview Session Flow

The complete workflow from question to feedback to final report:

```
┌─────────────────────────────────────────────────────────────────┐
│                   INTERVIEW SESSION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

STEP 1: START INTERVIEW
  → Load question bank for selected company
  → Pull first question from bank (Q1)
  → Display question to user (via Avatar component)

STEP 2: USER ANSWERS
  → Camera records answer (60 sec max)
  → User clicks "Submit Answer"
  → Video blob sent to Flask endpoint POST /api/submit-answer

STEP 3: BACKEND VIDEO PROCESSING (15-20 sec)
  ┌─────────────────────────────────────────┐
  │ Video Processor (Part 10)                │
  │                                         │
  │ • Extract audio via moviepy             │
  │ • Extract frames via OpenCV (2fps)      │
  │ • Send audio to Whisper API             │
  │ • Receive: transcript + word timestamps │
  │ • Calculate: WPM, pause_count,          │
  │             pause_duration, filler_count│
  │                                         │
  │ MediaPipe Analyzer (Part 11)            │
  │                                         │
  │ • Analyze frames for eye contact        │
  │ • Detect head pose & facial stability   │
  │ • Classify emotion (confident/nervous)  │
  │ • Check body posture                    │
  │                                         │
  │ EXTRACTED FEATURES (10 total):          │
  │ 1. transcript_length                    │
  │ 2. words_per_minute                     │
  │ 3. pause_count                          │
  │ 4. pause_avg_duration                   │
  │ 5. filler_word_count                    │
  │ 6. eye_contact_percent (0-100)          │
  │ 7. head_pose_score (0-10)               │
  │ 8. posture_score (0-10)                 │
  │ 9. facial_stability_score (0-10)        │
  │ 10. question_difficulty (1/2/3)         │
  │                                         │
  └─────────────────────────────────────────┘

STEP 4: YOUR TRAINED ML MODEL SCORES (milliseconds)
  ┌─────────────────────────────────────────┐
  │ ML Model Inference (Part 12)            │
  │                                         │
  │ Input: [10 features as array]           │
  │   ↓                                     │
  │ Load trained model from disk            │
  │ (answer_scoring_model.pkl via joblib)   │
  │   ↓                                     │
  │ model.predict([features])               │
  │   ↓                                     │
  │ Output: predicted_score (float 1-10)    │
  │                                         │
  │ Example:                                │
  │ Input: [120, 145, 2, 3.5, 5, 72, 7, 8, │
  │         8, 2]                           │
  │ → Model outputs: 6.8/10                 │
  │                                         │
  └─────────────────────────────────────────┘

STEP 5: GEMINI FOLLOW-UP (5-10 sec)
  ┌─────────────────────────────────────────┐
  │ LLM Evaluator (Part 12)                 │
  │                                         │
  │ Send to Gemini API:                     │
  │ • original_question                     │
  │ • user_transcript                       │
  │ • model_predicted_score (e.g., 6.8)     │
  │ • question_difficulty                   │
  │ • cv_data (skills, experience)          │
  │                                         │
  │ Gemini processes:                       │
  │ • If score < 5: probe deeper            │
  │ • If score ≥ 7: explore advanced topics │
  │ • Generate 1 intelligent follow-up Q    │
  │                                         │
  │ Gemini also identifies:                 │
  │ • 2 strengths (from transcript+score)   │
  │ • 1 key improvement area                │
  │                                         │
  │ Return:                                 │
  │ • follow_up_question (string)           │
  │ • strengths (list)                      │
  │ • improvements (list)                   │
  │                                         │
  └─────────────────────────────────────────┘

STEP 6: NEXT QUESTION DECISION
  → Count questions answered so far
  → Is this the final question (Q5 or Q7)?
  
  NO → Continue interview loop:
    • Show 3-bullet quick feedback:
      - Score: 6.8/10
      - Strength: "clear communication"
      - Improvement: "add more technical depth"
    • Display follow-up question from Gemini
    • User answers → Go back to STEP 3
  
  YES → Go to STEP 7

STEP 7: SESSION COMPLETE & FINAL REPORT
  ┌──────────────────────────────────────────┐
  │ Session Summary (Part 9 + Part 12)       │
  │                                          │
  │ Aggregate all question scores:           │
  │ • Q1 score: 6.8                          │
  │ • Q2 score: 7.2                          │
  │ • Q3 score: 5.9                          │
  │ • Q4 score: 7.5                          │
  │ • Q5 score: 6.4                          │
  │ → Final Score = average = 6.76/10        │
  │                                          │
  │ Collect all data:                        │
  │ • All transcripts                        │
  │ • All model scores                       │
  │ • All behavioral metrics                 │
  │ • Company + Role + Experience            │
  │                                          │
  │ Send to Gemini for final assessment:     │
  │ • Overall performance summary            │
  │ • Key strengths demonstrated            │
  │ • Top 3 actionable recommendations       │
  │ → Get back: 3-paragraph written report   │
  │                                          │
  │ Save to Firestore:                       │
  │ • session_id, user_id, company, role     │
  │ • all_transcripts, all_scores            │
  │ • final_score, final_report              │
  │ • timestamp, duration                    │
  │                                          │
  └──────────────────────────────────────────┘
         ↓
  Frontend displays final report:
  • Large overall score (6.76/10)
  • Per-dimension breakdown (5 bars)
  • Written assessment from Gemini
  • Strengths list
  • Improvements list
  • Save/download options
  • Add to interview history

```

---

## 3. Core User Flow

```
Landing Page
    ↓
Sign Up / Log In (Firebase Auth)
    ↓
Upload CV (PDF → Firebase Storage → Python Parser)
    ↓
CV analyzed → Role & Company suggestions shown
    ↓
User selects Company + Role + Experience Level
    ↓
Interview briefing shown:
  "Microsoft conducts a 10-question interview covering DSA,
   system design, and behavioral. Here's what to expect..."
    ↓
Interview Room Opens
  → AI Avatar (stick figure, React/CSS) appears
  → Avatar speaks/displays Question 1
  → User clicks "I'm Ready"
  → Avatar minimizes to corner (PiP)
  → Camera opens, recording starts
  → User answers
  → User clicks "Submit Answer"
  → Quick 3-bullet feedback shown
  → Next question loads
  ↓
All questions done
    ↓
Full Session Report (scores, breakdown, recommendations)
    ↓
Report saved to user profile (history)
```

---

## 3. Company & Question Bank

### Question Bank Structure (per company)
Each company entry contains:
- Interview process description (rounds, format, duration)
- Question bank: 20–30 questions tagged by type
- Evaluation criteria specific to that company

```json
{
  "company": "[Company Name — TBD]",
  "process": "Interview process description: rounds, format, duration",
  "total_questions_in_interview": 10,
  "question_bank": [
    {
      "id": "[company_code]_001",
      "question": "Sample question text",
      "type": "behavioral | technical | situational | system_design",
      "difficulty": "easy | medium | hard",
      "what_they_look_for": "Evaluation criteria — what interviewers prioritize in the answer"
    }
  ]
}
```

### How to Build the Question Bank
Assign one team member to this task. Method:
1. Decide on target companies (international + local)
2. For each company: research interview process, question types, and difficulty distribution
3. Use AI tools (ChatGPT / Gemini) to generate initial questions based on community data (Glassdoor, LeetCode, interview blogs)
4. Manually verify each question — ensure relevance and accuracy
5. Tag every question: `type` (behavioral / technical / situational / system_design), `difficulty` (easy / medium / hard), `what_they_look_for` (1–2 sentences on ideal answer)
6. Store as structured JSON files in `/backend/data/question_banks/`
7. This is a deliverable in itself — treat it like a dataset
- Deliverable: N complete JSON files (one per company), ~25–30 verified questions each, company list finalized

---

---

## 7. What Your Trained Model Does

**Problem it solves:** You need to evaluate interview answers in a way that's consistent, fast, and understandable to the course evaluators. While Gemini can generate text, we need a trained ML model to satisfy the AI course requirement.

**The model:** A regression model (Random Forest or Neural Network) trained on 100 labeled interview answers.

**Input:** 10 numerical features extracted from video/audio:
- Transcript length, words-per-minute, pause count, pause duration, filler word count
- Eye contact percentage, head pose score, posture score, facial stability score
- Question difficulty

**Output:** Predicted answer score (1.0–10.0)

**How it works in the app:**
1. After user submits video answer
2. Extract the 10 features from Whisper (audio) + MediaPipe (video)
3. Feed features to your trained model → get predicted_score (e.g., 5.3/10)
4. Send transcript + model_score to Gemini
5. Gemini generates adaptive follow-up question based on score + answer quality
6. At end of interview: aggregate all model_scores into final report

**Why this approach:**
- Your trained model does the "heavy lifting" ML part (course requirement ✅)
- Gemini handles conversational intelligence and personalization
- Model is fast (milliseconds), cheap (no API calls), and interpretable
- Demonstrates both ML fundamentals AND LLM integration

---

## 8. Video Analysis — What We Extract

### From Video Frames (MediaPipe)

| Signal | Method | What It Measures |
|---|---|---|
| Eye Contact | Face mesh → gaze direction vector | Is the user looking at the camera or away? |
| Facial Confidence | Landmark variance over time | Stable face = composed, excessive movement = nervous |
| Emotion | MediaPipe Face Mesh + heuristics (brow, mouth corners) | Confident, nervous, confused, neutral |
| Head Pose | 3D head orientation from face landmarks | Upright = engaged, looking down = unsure |
| Body Posture | Pose estimation (shoulders, spine angle) | Slouching vs. upright, open vs. closed body |

### From Audio (Whisper API)

| Signal | Method | What It Measures |
|---|---|---|
| Transcript | Whisper speech-to-text | Full text of answer |
| Speaking Pace | Words per minute from timestamps | Too fast (nervous) or too slow (unsure) |
| Pause Detection | Silence gap analysis | Long pauses = struggling, thinking |
| Filler Words | Text scan post-transcription | Count of "um", "uh", "like", "you know" |

---

## 9. Scoring System

### Per-Question Scores (out of 10 each)

| Dimension | What's Evaluated | Source |
|---|---|---|
| **Content Quality** | Relevance, depth, structure (STAR for behavioral) | LLM (Gemini) on transcript |
| **Communication** | Clarity, vocabulary, no filler words, sentence structure | LLM + filler word count |
| **Confidence** | Eye contact %, head pose stability, emotion reading | MediaPipe analysis |
| **Body Language** | Posture score, movement consistency | MediaPipe pose |
| **Pace & Delivery** | WPM in ideal range (130–160), pause distribution | Whisper timestamps |

### Final Session Score
```
Overall = (Content×0.35) + (Communication×0.25) + (Confidence×0.20) + (Body Language×0.10) + (Pace×0.10)
```

### Sample Report Output
```
📊 Mock Interview Report — Microsoft | SWE Intern

Overall Score: 74/100 — Good  

Content Quality:    8.1/10   ████████░░
Communication:      7.4/10   ███████░░░
Confidence:         6.8/10   ██████░░░░
Body Language:      7.0/10   ███████░░░
Pace & Delivery:    7.5/10   ███████░░░

✅ Strengths
  • Strong technical depth in DSA questions
  • Maintained eye contact 71% of the time
  • Good use of STAR format in behavioral answers

⚠️ Areas to Improve
  • Reduce filler words (detected 14x "um/uh")
  • Speaking pace too fast in Q3 (192 WPM — target: 130–160)
  • Body posture: slouching detected in 3 of 5 questions

💡 Recommendations
  1. Practice pausing instead of using fillers
  2. Record yourself answering and watch back
  3. Sit back and open your shoulders before the interview starts
```

---

## 10. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   REACT FRONTEND                    │
│  Auth Pages · CV Upload · Interview Room · Reports  │
│              Hosted on: Vercel                      │
└────────────────────┬────────────────────────────────┘
                     │ HTTP (REST API calls)
┌────────────────────▼────────────────────────────────┐
│               FLASK BACKEND (Python)                │
│                                                     │
│  /api/parse-cv        → CV Parser Module            │
│  /api/start-session   → Question Generator          │
│  /api/submit-answer   → Video Processor             │
│                         + AI Analysis Engine        │
│                         + LLM Evaluator             │
│  /api/end-session     → Session Manager + Report    │
│                                                     │
│              Hosted on: Render                      │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
  Firebase         Whisper        Gemini
  Auth/DB/Store    API            API
  (Google)         (OpenAI)       (Google)
       │
  MediaPipe
  (local in Flask)
```

---

## 11. Updated Tech Stack

| Layer | Technology | Purpose | ML Training |
|---|---|---|---|
| Frontend | React + CSS | UI, webcam capture, avatar | — |
| Auth + DB | Firebase Auth + Firestore | User accounts, session history | — |
| File Storage | Firebase Storage | CV uploads | — |
| Backend | Flask (Python) | API layer, orchestration | — |
| CV Parsing | PyMuPDF + spaCy | Extract text from PDF CV | — |
| Video Analysis | MediaPipe | Face, pose, emotion from frames | — |
| Transcription | OpenAI Whisper API | Speech to text with timestamps | — |
| **Answer Scoring** | **Scikit-learn (Random Forest / Neural Network)** | **Predict answer score 1-10 from 10 features** | **✅ YES** |
| LLM Brain | Google Gemini API | Question generation + adaptive follow-ups | — |
| Hosting (BE) | Render | Flask app (free tier) | — |
| Hosting (FE) | Vercel | React app (free tier) | — |

---

## 8. Updated Complete Workflow (With Trained Model)

```
User uploads CV → parses skills/experience
         ↓
User selects role + company
         ↓
System loads question bank for that company
         ↓
INTERVIEW LOOP — 5-7 questions
  Question pulled from question bank
         ↓
  User answers on camera (60 sec)
         ↓
  Video processing: extract audio + frames
  Whisper: transcribe → get transcript + timestamps
  MediaPipe: analyze frames → get behavioral signals (eye contact, posture, emotion, etc)
         ↓
  Extract 10 features: transcript_length, WPM, pause_count, filler_count, 
  eye_contact_pct, head_pose_score, posture_score, facial_stability_score, 
  question_difficulty
         ↓
  YOUR TRAINED MODEL predicts score (1-10)
         ↓
  Send transcript + model_score to Gemini
  Gemini generates adaptive follow-up question based on answer quality
         ↓
  Next iteration: show follow-up question OR load next main question
         ↓
All 5-7 questions completed
         ↓
Session summary: aggregate all model_scores
         ↓
Gemini generates final 3-paragraph assessment
         ↓
FINAL REPORT shown: Overall score, per-dimension breakdown, strengths, improvements
         ↓
Report saved to Firestore
```

---

## 9. Project Divided Into 12 Parts Across 4 Categories

Each category maps to a distinct skill set. Assign 3 parts per team member — ideally keeping each person within one or two categories so there's no context switching.

---

### Category A — Research & Non-Tech Work
*No coding required. Data, content, and documentation.*

#### Part 1 — Company Research & Interview Process Documentation
- Research target companies (to be finalized by team) and document for each: number of rounds, round types (DSA, behavioral, system design, HR), average duration, what interviewers prioritize, tips from real candidates
- Sources: Glassdoor, LinkedIn, LeetCode discuss, interview experience blogs, Reddit
- Output: structured Google Doc first, then formatted into JSON metadata fields per company
- This content powers the "Interview Briefing" page the user reads before starting
- Deliverable: completed metadata block for all finalized companies

#### Part 2 — Question Bank Curation & Verification
- Using Part 1 research, build the actual question sets per company
- Use AI tools (ChatGPT / Gemini) to generate an initial set of questions per company based on community data
- Manually verify each question — remove anything that feels generic or unverified
- Tag every question: `type` (behavioral / technical / situational / system_design), `difficulty` (easy / medium / hard), `what_they_look_for` (1–2 sentences on ideal answer)
- **Note:** Collection metrics (how many questions per company, type distribution, difficulty balance) to be finalized by team
- Final output: clean JSON files, one per company, stored in `/backend/data/question_banks/`
- Deliverable: N complete JSON files (one per finalized company), ~25–30 verified questions each

#### Part 3 — LaTeX Report & Technical Documentation
- The course requires a formal technical report in LaTeX
- Owner starts this from Week 1 — not Week 5
- Sections to maintain throughout: Abstract, Introduction, Methodology, System Architecture (with diagrams), Video Analysis Approach, Scoring System, Evaluation Results, Challenges, Conclusion
- Architecture diagrams drawn in draw.io or Excalidraw, exported and embedded
- Evaluation section filled in during Week 4 with real test results
- Deliverable: complete LaTeX report ready for submission

---

### Category B — UI/UX & Frontend Design
*React, CSS, browser APIs. No Python.*

#### Part 4 — Auth Pages & User Dashboard UI
- Login page, signup page, password reset page — all wired to Firebase Auth
- After login: dashboard showing CV upload status, company/role selector, past session history cards
- CV upload component: drag-and-drop PDF, upload progress bar, confirmation state
- Protected route logic: any page other than login/signup redirects to login if not authenticated
- Firebase SDK integration in React (`firebase.js` config file)
- Deliverable: fully working auth flow + dashboard shell

#### Part 5 — Interview Room UI & Avatar
- AI Avatar component: clean CSS character (stick figure or illustrated) that lives on screen
- Avatar displays question as text below it + speaks via Web Speech API (browser native, free, no API key)
- Two buttons: "I'm Ready" and "Skip Question"
- On "I'm Ready": avatar animates to small picture-in-picture corner, webcam opens full screen via `getUserMedia`
- Recording begins via `MediaRecorder API`, visual recording indicator shown
- "Submit Answer" button stops recording, sends video blob to Flask via `fetch POST`
- Loading state component while backend processes (~10–15 sec)
- Quick feedback card: 3 bullet points (2 strengths, 1 tip) slides in before next question
- Deliverable: complete interview room that records and submits video

#### Part 6 — Score Report & History UI
- Full session report page: overall score as large number + grade label, per-dimension progress bars (5 dimensions), written assessment paragraph from Gemini, strengths list, improvements list, company-specific closing tips
- Per-question breakdown accordion: expand each question to see its individual scores
- Session history page: list of all past interviews pulled from Firestore, each showing company, role, date, overall score — clickable to view full report
- Download report as PDF using `jsPDF` library
- Responsive design — works on mobile too
- Deliverable: complete report and history pages

---

### Category C — Coding & Backend Logic
*Pure Python. Flask, data processing, business logic.*

#### Part 7 — Flask API Setup & Firebase Admin Integration
- `app.py`: initialize Flask app, define all routes (even if empty at first), configure CORS so React can call it
- Firebase Admin SDK setup: verify user auth tokens on protected endpoints, read/write Firestore, access Storage
- All environment variables loaded from `.env` (API keys never hardcoded)
- Standard response format defined: `{"success": true, "data": {...}}` or `{"success": false, "error": "..."}`
- Request validation on all endpoints: check required fields, return clear errors if missing
- This file is the backbone — build it first so other backend members can plug their modules in
- Deliverable: fully scaffolded `app.py` with all routes, middleware, and Firebase connection working

#### Part 8 — CV Parser
- Flask endpoint `POST /api/parse-cv` receives PDF file
- `PyMuPDF (fitz)` extracts raw text from all pages
- Parsing logic extracts: full name, email, skills list, years of experience (calculated from dates), education level (bachelor/master/etc), domain (CS / Data Science / Finance / Marketing etc)
- Company and role suggestions generated from skills + domain match against a mapping dict
- Returns structured JSON: `{"name": "...", "skills": [...], "suggested_companies": [...], "experience_years": X}`
- Standalone module `cv_parser.py` — imported and called by `app.py`
- Deliverable: working CV parser tested on 3–4 sample CVs

#### Part 9 — Session & Question Manager
- `POST /api/start-session`: takes company + role + experience level, loads correct question bank JSON, selects N questions (type-balanced: not all behavioral, not all technical), shuffles, creates session object in Firestore, returns question list to frontend
- Session object in Firestore: `{user_id, company, role, questions[], answers[], scores[], status, created_at}`
- `POST /api/end-session`: aggregates all per-question scores using weighted formula, calls LLM Evaluator for final written report, saves complete session to Firestore, returns final report JSON
- CV suggestion logic: maps parsed CV skills to companies and roles in the question bank
- Standalone module `session_manager.py` + `question_manager.py`
- Deliverable: complete session lifecycle from start to saved report

---

### Category D — LLM & AI Integration + ML Model
*APIs, MediaPipe, Whisper, Gemini, scikit-learn. The intelligence layer. Highest technical complexity.*

#### Part 10 — Video Processor
- `POST /api/submit-answer` receives video blob from React
- `moviepy` separates audio track → saves as `.wav`
- `OpenCV` extracts frames at 2fps → list of image arrays
- Sends `.wav` to Whisper API → receives transcript text + word-level timestamps
- From timestamps: calculates WPM, detects pauses longer than 2 seconds (count + avg duration), scans transcript text for filler words (`um`, `uh`, `like`, `you know`, `basically`, `literally`) and counts occurrences
- Packages everything into one signals dict: `{"transcript": "...", "wpm": 145, "pause_count": 3, "filler_count": 7, "frames": [...]}`
- Passes frames list to Part 11 (MediaPipe module), receives behavioral scores back
- Merges all signals into final dict → passes to Part 12 (Evaluator)
- Standalone module `video_processor.py`
- Deliverable: working processor tested on local video files, outputs complete signals dict

#### Part 11 — MediaPipe Behavioral Analysis
- Receives frames list from Part 10
- **Eye Contact**: MediaPipe Face Mesh on each frame → extract iris landmarks → calculate gaze direction vector → compare to camera-facing vector → classify each frame as "looking at camera" or not → eye_contact_pct = (looking frames / total frames) × 100
- **Head Pose**: 3D head orientation from face landmarks → classify upright vs tilted → head_pose_score (0–10)
- **Facial Stability**: variance of key landmark positions across frames → low variance = composed, high = nervous → stability_score (0–10)
- **Emotion**: heuristics from brow landmarks (raised = surprised/nervous) and mouth corners (up = positive, down = stressed) → dominant_emotion string
- **Posture**: MediaPipe Pose on sampled frames → shoulder landmark y-positions → detect slouch → posture_score (0–10)
- Returns: `{"eye_contact_pct": 68, "head_pose_score": 7, "stability_score": 8, "dominant_emotion": "confident", "posture_score": 6}`
- Standalone module `mediapipe_analyzer.py` — fully testable with any webcam video
- Deliverable: working analyzer tested on sample videos, outputs clean behavioral dict

#### Part 12 — ML Model Training & LLM Evaluator + Report Generator
**ML Model Training (core deliverable for AI course):**
- Write/collect 100 realistic interview answers (or use Part 10/11 pipeline to generate them)
- For each answer: simulate behavioral signals (WPM, pauses, eye contact, posture, etc.) realistically
- Call Gemini API to label each answer with a quality score (1-10)
- Compile into `dataset.csv`: 100 rows × 10 features (transcript_length, WPM, pause_count, pause_duration, filler_count, eye_contact_pct, head_pose_score, posture_score, facial_stability_score, question_difficulty) + target score
- Train Random Forest Regressor on 80 examples, test on 20 held-out examples using `scikit-learn`
- Evaluate: compute MAE (target: < 1.0), R² (target: > 0.85), feature importances
- Save trained model as `answer_scoring_model.pkl` using `joblib`
- Standalone modules: `ml/train_model.py`, `ml/generate_dataset.py`, `ml/evaluate_model.py`

**Model Integration (runtime inference):**
- `evaluator.py` imports the trained `.pkl` model
- Receives: question object + full signals dict (transcript + behavioral scores) from Parts 10 & 11
- **Feeds 10 features into the trained model → model predicts answer_score (1-10)**
- Sends predicted_score + transcript to Gemini API for adaptive follow-up generation
- Applies weighted scoring formula for session summary: `Overall = (Content×0.35) + (Communication×0.25) + (Confidence×0.20) + (Body×0.10) + (Pace×0.10)`
- Returns per-question result: predicted_score + strengths list + improvements list
- **Session summary**: called by Part 9 at end of session — receives all Q&A data + model scores → constructs summary prompt → calls Gemini → returns 3-paragraph written assessment
- All prompt templates maintained in `prompts.py` (never hardcoded inline)
- Standalone modules: `evaluator.py`, `prompts.py`, and `ml/` subfolder
- Deliverable: trained `.pkl` model with test metrics (MAE, R², feature analysis) + working evaluator tested on sample transcripts, returns correct JSON structure

---

### Quick Reference — All 12 Parts

| # | Part Name | Category | Output |
|---|---|---|---|
| 1 | Company Research & Process Docs | Research | JSON metadata per company |
| 2 | Question Bank Curation | Research | 10–12 JSON question bank files |
| 3 | LaTeX Report & Documentation | Research | Complete technical report |
| 4 | Auth Pages & Dashboard UI | UI/UX | Working auth flow + dashboard |
| 5 | Interview Room UI & Avatar | UI/UX | Webcam recording + avatar |
| 6 | Score Report & History UI | UI/UX | Report page + history page |
| 7 | Flask API Setup & Firebase | Coding | Scaffolded backend + DB connection |
| 8 | CV Parser | Coding | `cv_parser.py` + endpoint |
| 9 | Session & Question Manager | Coding | Full session lifecycle |
| 10 | Video Processor | LLM/AI | Signals dict from video |
| 11 | MediaPipe Behavioral Analysis | LLM/AI | Behavioral scores dict |
| 12 | ML Model Training + LLM Evaluator & Report Generator | LLM/AI | Trained `.pkl` model + scores + written report |

### Suggested Assignment (3 parts per person)

| Person | Parts | Category Focus |
|---|---|---|
| Member A | 1, 2, 3 | Pure research + documentation |
| Member B | 4, 5, 6 | Full frontend |
| Member C | 7, 8, 9 | Full backend logic |
| Member D | 10, 11, 12 | Full AI pipeline + ML model training |

---

## 9. Key Prompt Templates (Gemini Integration)

### Follow-Up Question Generation Prompt (used after each answer)
```
You are conducting an interview. The candidate just answered a question 
and received a score of {model_score}/10 from our ML evaluation model.

ORIGINAL QUESTION:
"{question}"

CANDIDATE'S ANSWER:
"{transcript}"

CANDIDATE BACKGROUND:
- Target Role: {role}
- Company: {company}
- Skills: {skills}
- Experience: {years_experience} years

The ML model scored this answer {model_score}/10 based on:
- Speaking clarity, pace, and confidence signals
- Eye contact: {eye_contact_pct}%
- Filler words: {filler_count}
- Pauses and hesitation patterns

Your task: Generate ONE intelligent follow-up question that:
1. Probes deeper into what they said
2. Is personalized to their CV and background
3. Naturally advances the interview
4. Matches the difficulty level of the previous question

If the score is low (< 5): push for clarification or deeper understanding
If the score is high (≥ 7): explore related advanced topics

Respond ONLY with the follow-up question text. No explanation needed.
```

### Session Summary Prompt (used at end of interview)
```
You are generating a final interview assessment report.

INTERVIEW DETAILS:
- Company: {company}
- Role: {role}
- Total Questions: {total_questions}

QUESTION-BY-QUESTION SCORES (from ML model):
{all_scores_json}

OVERALL STATISTICS:
- Average Score: {avg_score}/10
- Highest Score: {max_score}/10
- Lowest Score: {min_score}/10

Based on all transcripts and scores, write a professional 3-paragraph 
assessment covering:
1. Overall performance summary and readiness for this role
2. Key strengths demonstrated
3. Top 3 actionable recommendations for improvement

Be honest, specific, and encouraging. Use real examples from the interview.
```

---

## 12. Folder Structure

```
mock-interviewer/
├── backend/
│   ├── app.py                          # Flask app — all routes (Part 7)
│   │                                   #   POST /api/parse-cv
│   │                                   #   POST /api/start-session
│   │                                   #   POST /api/submit-answer
│   │                                   #   POST /api/end-session
│   ├── cv_parser.py                    # Part 8 — CV text extraction + structured output
│   ├── question_manager.py             # Part 9 — load + shuffle question bank per company
│   ├── session_manager.py              # Part 9 — Firestore session lifecycle
│   ├── video_processor.py              # Part 10 — audio/frame extraction, Whisper, WPM/pause/filler
│   ├── mediapipe_analyzer.py           # Part 11 — eye contact, posture, emotion, head pose
│   ├── evaluator.py                    # Part 12 — ML model inference + Gemini LLM calls
│   ├── prompts.py                      # Part 12 — all Gemini prompt templates (never inline)
│   ├── ml/
│   │   ├── train_model.py              # Part 12 — script to generate dataset + train Random Forest
│   │   ├── generate_dataset.py         # Part 12 — writes 100 answers, simulates signals, calls Gemini for labels
│   │   ├── dataset.csv                 # Part 12 — 100 labeled training examples (10 features + score)
│   │   ├── answer_scoring_model.pkl    # Part 12 — trained Random Forest saved with joblib
│   │   └── evaluate_model.py           # Part 12 — computes MAE, R², feature importances on test set
│   ├── data/
│   │   └── question_banks/
│   │       ├── company_1.json
│   │       ├── company_2.json
│   │       ├── company_3.json
│   │       └── ... (more companies as decided)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Avatar.jsx              # Part 5 — CSS avatar + Web Speech API
│   │   │   ├── InterviewRoom.jsx       # Part 5 — webcam, MediaRecorder, submit flow
│   │   │   ├── ScoreCard.jsx           # Part 6 — per-question score breakdown
│   │   │   ├── FinalReport.jsx         # Part 6 — overall report, progress bars, Gemini summary
│   │   │   └── CVUpload.jsx            # Part 4 — drag-and-drop PDF upload UI
│   │   ├── pages/
│   │   │   ├── Login.jsx               # Part 4 — Firebase Auth login
│   │   │   ├── Signup.jsx              # Part 4 — Firebase Auth signup
│   │   │   ├── Dashboard.jsx           # Part 4 — company/role selector + CV status
│   │   │   ├── Interview.jsx           # Part 5 — interview room page wrapper
│   │   │   └── History.jsx             # Part 6 — past sessions from Firestore
│   │   ├── firebase.js                 # Firebase config (Auth + Firestore + Storage)
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## 13. Hosting Setup

### Backend — Render (Free)
1. Push backend folder to GitHub
2. Create new Web Service on render.com
3. Connect GitHub repo, set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables (API keys) in Render dashboard

### Frontend — Vercel (Free)
1. Push frontend folder to GitHub
2. Import project on vercel.com
3. Set framework to React, build command `npm run build`
4. Add `REACT_APP_API_URL` env variable pointing to Render backend URL

### Firebase Setup
1. Create project on Firebase Console
2. Enable Authentication (Email + Google)
3. Enable Firestore Database
4. Enable Storage (for CV uploads)
5. Add Firebase config to `frontend/src/firebase.js`

---

## 14. Evaluation Metrics (for AI course report)

- **Answer evaluation accuracy**: manually rate 20 sample answers, compare to system scores
- **Transcription accuracy**: WER (Word Error Rate) from Whisper on test recordings
- **Model evaluation metrics**: MAE (Mean Absolute Error) < 1.0, R² > 0.85 on test set
- **Bias check**: test system on answers of varying lengths and quality, verify scores correlate correctly
- **Latency**: measure time from "Submit Answer" to model prediction (target: < 2 seconds)

---

## 15. Pitch

"Our Mock Interviewer project is a **hybrid AI system** combining trained ML models with LLM APIs:

**The Machine Learning Component (your trained model):**
We built a **regression model** (Random Forest Regressor) that predicts interview answer quality on a scale of 1-10. The model is trained on a labeled dataset of 100 interview answers collected via:
1. Writing/collecting realistic interview answer samples
2. Simulating behavioral signals (eye contact, speaking pace, pauses) realistically
3. Labeling each answer with a quality score using Gemini API
4. Training on 80 examples, testing on 20 held-out examples

**Model input features (10 total):**
- Linguistic: transcript length, WPM, pause count, pause duration, filler word count
- Behavioral: eye contact %, head pose score, posture score, facial stability score (from MediaPipe)
- Contextual: question difficulty

**Model output:** Predicted score (1-10) with MAE < 1.0 and R² > 0.85

**Integration with LLM APIs:**
During interviews, after the user answers a question:
1. We extract 10 features from the video/audio using Whisper and MediaPipe
2. Our trained model predicts the answer's quality score
3. We send the model's score + transcript to Gemini
4. Gemini uses the score to generate adaptive, personalized follow-up questions

**Why this approach demonstrates AI fundamentals:**
- ✅ We trained a regression model from scratch (ML requirement)
- ✅ We created a labeled training dataset (data science)
- ✅ We integrated it with LLMs for conversational intelligence
- ✅ We demonstrate both classical ML and modern AI/LLM knowledge

The trained model is the core ML deliverable. The LLM integration shows we understand how to combine classical ML with cutting-edge AI APIs in a real-world application."

---

*Document version 3.0 — Updated with trained model workflow, simplified planning phase*