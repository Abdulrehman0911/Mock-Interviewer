"""Flask API for Mock Interviewer with ML model integration."""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import our modules
import model_inference
import question_manager
import evaluator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all origins (development)

# Configuration
app.config["JSON_SORT_KEYS"] = False

print("=" * 60)
print("Mock Interviewer Flask API")
print("=" * 60)


# ============================================================================
# HEALTH CHECK & INFO ENDPOINTS
# ============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON: {"status": "ok"}
    """
    return jsonify({"status": "ok"}), 200


@app.route("/api/info", methods=["GET"])
def api_info():
    """
    Get API information.
    
    Returns:
        JSON: API version and available endpoints.
    """
    return jsonify({
        "success": True,
        "app": "Mock Interviewer",
        "version": "1.0",
        "status": "running"
    }), 200


# ============================================================================
# QUESTION MANAGEMENT ENDPOINTS
# ============================================================================

@app.route("/api/roles", methods=["GET"])
def get_roles():
    """
    Get all available job roles.
    
    Returns:
        JSON: {"success": true, "roles": [...]}
    """
    try:
        if question_manager.question_manager is None:
            return jsonify({
                "success": False,
                "error": "Question manager not initialized"
            }), 500

        roles = question_manager.get_all_roles()
        print(f"✓ Retrieved {len(roles)} roles")
        
        return jsonify({
            "success": True,
            "roles": roles,
            "count": len(roles)
        }), 200

    except Exception as e:
        print(f"✗ Error in /api/roles: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/questions/<role>", methods=["GET"])
def get_questions(role):
    """
    Get random interview questions for a specific role.
    
    Args:
        role (str): Job role name (path parameter)
    
    Query Parameters:
        count (int): Number of questions to return (default: 5)
    
    Returns:
        JSON: {"success": true, "questions": [...], "count": N}
    """
    try:
        count = request.args.get("count", 5, type=int)
        
        if count < 1 or count > 20:
            return jsonify({
                "success": False,
                "error": "Count must be between 1 and 20"
            }), 400

        questions = question_manager.get_random_questions(role, count)
        print(f"✓ Retrieved {len(questions)} questions for {role}")
        
        return jsonify({
            "success": True,
            "questions": questions,
            "count": len(questions),
            "role": role
        }), 200

    except ValueError as e:
        print(f"✗ Invalid role: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        print(f"✗ Error in /api/questions: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# ANSWER EVALUATION ENDPOINT
# ============================================================================

@app.route("/api/evaluate-answer", methods=["POST"])
def evaluate_answer_endpoint():
    """
    Evaluate an interview answer.
    
    Request Body:
        {
            "features": {
                "transcript_length": int,
                "wpm": float,
                "pause_count": int,
                "pause_avg_duration": float,
                "filler_count": int,
                "eye_contact_pct": float,
                "head_pose_score": int,
                "posture_score": int,
                "facial_stability_score": int,
                "question_difficulty": int
            },
            "transcript": "user's answer text",
            "question_id": int,
            "role": "Software Engineer"
        }
    
    Returns:
        JSON: {
            "success": true,
            "model_score": X.X,
            "follow_up_question": "...",
            "strengths": [...],
            "improvements": [...],
            "performance_level": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body cannot be empty"
            }), 400

        # Validate required fields
        required_fields = ["features", "transcript"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing)}"
            }), 400

        features = data.get("features")
        transcript = data.get("transcript")
        question_id = data.get("question_id")
        role = data.get("role", "Technical")

        # Validate features dict
        if not isinstance(features, dict):
            return jsonify({
                "success": False,
                "error": "Features must be a dictionary"
            }), 400

        # Validate transcript
        if not isinstance(transcript, str) or len(transcript.strip()) == 0:
            return jsonify({
                "success": False,
                "error": "Transcript must be a non-empty string"
            }), 400

        # Evaluate the answer
        evaluation = evaluator.evaluate_answer(features, transcript)
        
        print(f"✓ Evaluated answer for {role} (Q{question_id}): score={evaluation['model_score']}")

        return jsonify({
            "success": True,
            "model_score": evaluation["model_score"],
            "follow_up_question": evaluation["follow_up_question"],
            "strengths": evaluation["strengths"],
            "improvements": evaluation["improvements"],
            "performance_level": evaluation["performance_level"]
        }), 200

    except ValueError as e:
        print(f"✗ Validation error in /api/evaluate-answer: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except RuntimeError as e:
        print(f"✗ Runtime error in /api/evaluate-answer: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    except Exception as e:
        print(f"✗ Unexpected error in /api/evaluate-answer: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500


# ============================================================================
# SESSION SUMMARY ENDPOINT
# ============================================================================

@app.route("/api/session-summary", methods=["POST"])
def session_summary_endpoint():
    """
    Generate a summary report for an interview session.
    
    Request Body:
        {
            "scores": [8.5, 7.2, 6.1, ...],
            "transcripts": ["answer1", "answer2", ...],
            "role": "Software Engineer"
        }
    
    Returns:
        JSON: {
            "success": true,
            "overall_score": X.X,
            "average_score": X.X,
            "highest_score": X.X,
            "lowest_score": X.X,
            "total_questions": N,
            "performance_level": "...",
            "summary": "...",
            "statistics": {...}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body cannot be empty"
            }), 400

        # Validate required fields
        required_fields = ["scores", "transcripts"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing)}"
            }), 400

        scores = data.get("scores", [])
        transcripts = data.get("transcripts", [])
        role = data.get("role", "Technical")

        # Validate inputs
        if not isinstance(scores, list) or not isinstance(transcripts, list):
            return jsonify({
                "success": False,
                "error": "Scores and transcripts must be lists"
            }), 400

        if len(scores) == 0 or len(transcripts) == 0:
            return jsonify({
                "success": False,
                "error": "Scores and transcripts cannot be empty"
            }), 400

        if len(scores) != len(transcripts):
            return jsonify({
                "success": False,
                "error": "Number of scores must match number of transcripts"
            }), 400

        # Generate summary report
        report = evaluator.generate_summary_report(scores, transcripts)
        
        print(f"✓ Generated session summary for {role}: overall_score={report['overall_score']}")

        return jsonify({
            "success": True,
            "overall_score": report["overall_score"],
            "average_score": report["average_score"],
            "highest_score": report["highest_score"],
            "lowest_score": report["lowest_score"],
            "total_questions": report["total_questions"],
            "performance_level": report["performance_level"],
            "summary": report["summary"],
            "statistics": report["statistics"]
        }), 200

    except ValueError as e:
        print(f"✗ Validation error in /api/session-summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except RuntimeError as e:
        print(f"✗ Runtime error in /api/session-summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    except Exception as e:
        print(f"✗ Unexpected error in /api/session-summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    print()
    print("Starting Flask server...")
    print("Loading models and data...")
    
    # Verify models and data are loaded
    if model_inference.inference is None:
        print("⚠ WARNING: Model not loaded. Some endpoints will fail.")
    else:
        print("✓ Model loaded successfully")
    
    if question_manager.question_manager is None:
        print("⚠ WARNING: Questions not loaded. Some endpoints will fail.")
    else:
        print("✓ Questions loaded successfully")
    
    print()
    print("=" * 60)
    print("Server ready at http://localhost:5000")
    print("=" * 60)
    print()
    
    # Run Flask app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )

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