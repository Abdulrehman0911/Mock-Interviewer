"""Flask API for Mock Interviewer with ML model integration."""

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify

# Add bundled ffmpeg to PATH so moviepy/subprocess can find it
try:
    import imageio_ffmpeg as _iio_ffmpeg
    _ffmpeg_dir = os.path.dirname(_iio_ffmpeg.get_ffmpeg_exe())
    os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    print(f"[FFMPEG] Using bundled ffmpeg: {_ffmpeg_dir}")
except Exception as _e:
    print(f"[FFMPEG] Warning: could not add bundled ffmpeg to PATH: {_e}")
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import tempfile

# Import new pipeline modules
import video_processor

# Import our modules
import model_inference
import question_manager
import evaluator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Accept"],
    "supports_credentials": False,
}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    return response

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

        roles = question_manager.question_manager.get_all_roles()
        print(f"[OK] Retrieved {len(roles)} roles")
        
        return jsonify({
            "success": True,
            "roles": roles,
            "count": len(roles)
        }), 200

    except Exception as e:
        print(f"[ERROR] Error in /api/roles: {str(e)}")
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

        questions = question_manager.question_manager.get_random_questions(role, count)
        print(f"[OK] Retrieved {len(questions)} questions for {role}")
        
        return jsonify({
            "success": True,
            "questions": questions,
            "count": len(questions),
            "role": role
        }), 200

    except ValueError as e:
        print(f"[ERROR] Invalid role: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        print(f"[ERROR] Error in /api/questions: {str(e)}")
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
        
        print(f"[OK] Evaluated answer for {role} (Q{question_id}): score={evaluation['model_score']}")

        return jsonify({
            "success": True,
            "model_score": evaluation["model_score"],
            "follow_up_question": evaluation["follow_up_question"],
            "strengths": evaluation["strengths"],
            "improvements": evaluation["improvements"],
            "performance_level": evaluation["performance_level"]
        }), 200

    except ValueError as e:
        print(f"[ERROR] Validation error in /api/evaluate-answer: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except RuntimeError as e:
        print(f"[ERROR] Runtime error in /api/evaluate-answer: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    except Exception as e:
        print(f"[ERROR] Unexpected error in /api/evaluate-answer: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500


# ============================================================================
# VIDEO PROCESSING ENDPOINT
# ============================================================================


@app.route("/api/process-video", methods=["OPTIONS"])
def process_video_options():
    return "", 200


@app.route("/api/process-video", methods=["POST"])
def process_video_endpoint():
    """Process uploaded video answer and return complete scoring breakdown.

    Real pipeline: WebM → MP4 → Extract audio → Transcribe → Analyze behavior → Score.
    """
    try:
        print("\n" + "=" * 80)
        print(f"[API] Video processing request received")
        print(f"[API] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[API] Files: {list(request.files.keys())}")
        print(f"[API] Form: {dict(request.form)}")

        # Validate input
        if 'video' not in request.files:
            print(f"[API] ERROR: No video file in request")
            return jsonify({"success": False, "error": "No video file provided"}), 400

        # Parse parameters
        qid = request.form.get("question_id")
        try:
            question_id = int(qid) if qid else None
        except Exception:
            question_id = None

        question_text = request.form.get("question_text", "")

        qdiff = request.form.get("question_difficulty", 2)
        try:
            qdiff = int(qdiff)
            if qdiff < 1 or qdiff > 3:
                qdiff = 2
        except Exception:
            qdiff = 2

        role = request.form.get("role", "Software Engineer")
        print(f"[API] question_id={question_id}, difficulty={qdiff}, role={role}")

        # Save video to temp file
        video_file = request.files['video']
        temp_video_path = os.path.join(tempfile.gettempdir(), 'user_video.webm')
        print(f"[API] Saving video to: {temp_video_path}")
        video_file.save(temp_video_path)

        saved_size = os.path.getsize(temp_video_path)
        print(f"[API] Saved video size: {saved_size / 1024 / 1024:.2f} MB")

        # Process video through the real pipeline
        print(f"[API] Starting video processing pipeline...")
        result = video_processor.process_video(temp_video_path)

        features = result["features"]
        features["question_difficulty"] = qdiff
        transcript = result.get("transcript", "")

        print(f"[API] Pipeline complete. wpm={features.get('wpm', 0)}, eye_contact={features.get('eye_contact_pct', 0)}%")
        print(f"[API] Transcript ({len(transcript.split()) if transcript else 0} words): {transcript[:80]}...")

        # Real evaluation pipeline (behavioral model + correctness keyword matching)
        try:
            evaluation = evaluator.evaluate_answer(
                features,
                transcript,
                question_id,
                role,
                question_text=question_text,
            )
        except Exception as e:
            print(f"[API] ERROR: evaluation failed: {str(e)}")
            return jsonify({"success": False, "error": f"evaluation_failed: {str(e)}"}), 500

        response_data = {
            "success": True,
            "scores": {
                "behavioral": {
                    "score": evaluation["breakdown"]["behavioral"]["score"],
                    "out_of": 4,
                    "percentage": evaluation["breakdown"]["behavioral"]["percentage"],
                    "subscale": evaluation["breakdown"]["behavioral"]["subscale"],
                },
                "correctness": {
                    "score": evaluation["breakdown"]["correctness"].get("score", 0),
                    "out_of": 6,
                    "percentage": evaluation["breakdown"]["correctness"].get("percentage", 0),
                    "subscale": evaluation["breakdown"]["correctness"].get("subscale", 0),
                    "tier": evaluation["breakdown"]["correctness"].get("tier_matched", "NONE"),
                    "match_pct": evaluation["breakdown"]["correctness"].get("match_pct", 0),
                    "filler_count": evaluation["breakdown"]["correctness"].get("filler_count", 0),
                },
                "final": {
                    "score": evaluation["breakdown"]["final"]["score"],
                    "out_of": 10,
                    "percentage": evaluation["breakdown"]["final"]["percentage"],
                },
            },
            "transcript": transcript,
            "features": {
                "wpm": features.get("wpm", 0),
                "eye_contact_pct": features.get("eye_contact_pct", 0),
                "filler_count": features.get("filler_count", 0),
                "pause_count": features.get("pause_count", 0),
            },
            "feedback": {
                "follow_up_question": evaluation.get("follow_up_question"),
                "strengths": evaluation.get("strengths"),
                "improvements": evaluation.get("improvements"),
                "performance_level": evaluation.get("performance_level"),
            },
        }

        final = response_data["scores"]["final"]["score"]
        beh = response_data["scores"]["behavioral"]["score"]
        cor = response_data["scores"]["correctness"]["score"]
        print(f"[API] FINAL: behavioral={beh}, correctness={cor}, final={final}/10")
        print("=" * 80 + "\n")

        # Cleanup temp video
        try:
            os.remove(temp_video_path)
        except Exception:
            pass

        return jsonify(response_data), 200

    except Exception as e:
        import traceback
        print(f"[API EXCEPTION] {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        print("=" * 80 + "\n")
        return jsonify({"success": False, "error": str(e)}), 500


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
        
        print(f"[OK] Generated session summary for {role}: overall_score={report['overall_score']}")

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
        print(f"[ERROR] Validation error in /api/session-summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except RuntimeError as e:
        print(f"[ERROR] Runtime error in /api/session-summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    except Exception as e:
        print(f"[ERROR] Unexpected error in /api/session-summary: {str(e)}")
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
        print("[WARN] Model not loaded. Some endpoints will fail.")
    else:
        print("[OK] Model loaded successfully")
    
    if question_manager.question_manager is None:
        print("[WARN] Questions not loaded. Some endpoints will fail.")
    else:
        print("[OK] Questions loaded successfully")
    
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
