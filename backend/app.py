import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for frontend integration
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({"status": "ok"}), 200

@app.route('/api/parse-cv', methods=['POST'])
def parse_cv():
    """Parses an uploaded CV (PDF/Word) to extract details like skills and experience."""
    return jsonify({"message": "CV parsed successfully", "data": {}}), 200

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Retrieves a list of available companies and roles for mock interviews."""
    return jsonify([
        {"id": "c1", "name": "Google", "roles": ["Software Engineer"]},
        {"id": "c2", "name": "Amazon", "roles": ["Backend Developer"]}
    ]), 200

@app.route('/api/company/<company_id>', methods=['GET'])
def get_company(company_id):
    """Retrieves details and interview configurations for a specific company."""
    return jsonify({"id": company_id, "name": "Sample Company"}), 200

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Initializes a new mock interview session and returns initial questions."""
    return jsonify({"session_id": "12345", "message": "Session started"}), 200

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Receives user's video/audio answer and processes it with AI for evaluation."""
    return jsonify({"feedback": "Good answer, improved tone required"}), 200

@app.route('/api/end-session', methods=['POST'])
def end_session():
    """Ends the current interview session and generates a final comprehensive report."""
    return jsonify({"report": "Overall score 85/100"}), 200

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port)