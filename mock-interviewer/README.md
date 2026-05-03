# Mock Interviewer

An AI-driven mock interview platform that simulates real technical interviews using video analysis, CV parsing, and generative AI feedback.

## Tech Stack

| Frontend | Backend | AI & Media | Data & Cloud |
| -------- | ------- | ---------- | ------------ |
| React, React Router | Python, Flask, Gunicorn | OpenAI, Gemini API, MediaPipe, NLP (spaCy) | Firebase, dotenv |

## Local Setup

### Backend (Python/Flask)
1. Navigate to the backend directory:
   `cd backend`
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv && venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys (see Environment Variables section).
5. Run the server:
   `python app.py`

### Frontend (React)
1. Navigate to the frontend directory:
   `cd frontend`
2. Install dependencies:
   `npm install`
3. Start the development server:
   `npm start`

## Environment Variables
The backend relies on the environment variables shown in `backend/.env.example`. Create a `.env` file in the `backend` folder containing your `GEMINI_API_KEY`, `OPENAI_API_KEY`, and `FIREBASE_*` credentials.

## Git Conventions

### Branch Naming
Please use the following format: `feature/[part-number]-[description]`
Example: `feature/A-cv-parser`

### Commit Messages
Format: `type: description`
Examples:
- `feat: added user authentication`
- `fix: resolved CORS issue on cv upload`
- `docs: updated readme instructions`
- `chore: updated dependencies`

## Team & Responsibilities

| Name | Section | Responsibilities & Roadmap |
| ---- | ------- | ---------------- |
| **Adil** | Section A | **Frontend & System Config:** Sets up React/Flask environments, implements base pages, handles initial API routing & CV upload interface. |
| **Asad** | Section B | **Database & Auth:** Integrates Firebase Authentication, manages user session states, sets up database schema for questions and user histories. |
| **Usman** | Section C | **Media & UI Interaction:** Video/Audio recording logic, MediaPipe integration for real-time tracking, WebRTC/Canvas management. |
| **AbdulRehman** | Section D | **Full AI Pipeline:** Implements CV parsing, Gemini/OpenAI prompt integration, answer analysis, feedback generation, and overall evaluator matrix. |

> Note: Make sure to review the full `plan.md` (if available) for granular step-by-step duties.