from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import os

load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return {"message": "Mock Interviewer API is running"}

@app.route('/api/parse-cv', methods=['POST'])
def parse_cv():
    return {"message": "CV parser endpoint — coming in Part 8"}

@app.route('/api/start-session', methods=['POST'])
def start_session():
    return {"message": "Session start endpoint — coming in Part 9"}

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    return {"message": "Submit answer endpoint — coming in Part 9"}

@app.route('/api/end-session', methods=['POST'])
def end_session():
    return {"message": "End session endpoint — coming in Part 9"}

if __name__ == '__main__':
    app.run(debug=True, port=5000)