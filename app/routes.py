# routes.py
# Defines all the URL endpoints your API exposes.
# Think of each @route as a "door" the frontend can knock on.

from flask import Blueprint, jsonify, request
from app.medicine_lookup import fetch_medicine_info, fetch_local_medicine
import json
import os

# Blueprint = a group of related routes
medicine_bp = Blueprint("medicine", __name__)


# ── ROUTE 1: Health Check ─────────────────────────────────────
@medicine_bp.route("/", methods=["GET"])
def health_check():
    """
    Simple check to confirm the server is running.
    Visit http://localhost:5000/ in your browser to test.
    """
    return jsonify({
        "status": "running",
        "message": "DoseAI Backend is live 🚀",
        "version": "1.0.0"
    })


# ── ROUTE 2: Medicine Lookup ──────────────────────────────────
@medicine_bp.route("/medicine/<string:name>", methods=["GET"])
def get_medicine(name):
    """
    Fetches medicine info by name.
    
    URL pattern: /medicine/ibuprofen
    Returns: JSON with usage, dosage, side_effects, overdose, warnings
    
    Strategy:
    1. First try local JSON (fast, works offline, covers Indian medicines)
    2. If not found locally, try OpenFDA API
    3. If neither works, return a clear error
    """
    
    medicine_name = name.lower().strip()
    
    # Step 1: Try local database first
    local_result = fetch_local_medicine(medicine_name)
    if local_result and "error" not in local_result:
        local_result["source"] = "local"  # Tag the source
        return jsonify(local_result), 200
    
    # Step 2: Try OpenFDA API
    api_result = fetch_medicine_info(medicine_name)
    if "error" not in api_result:
        api_result["source"] = "openFDA"
        return jsonify(api_result), 200
    
    # Step 3: Not found anywhere
    return jsonify({
        "error": f"Medicine '{name}' not found in local database or OpenFDA.",
        "suggestion": "Check spelling, or try the generic name (e.g., 'paracetamol' instead of 'Dolo 650')"
    }), 404


# ── ROUTE 3: Search with Query Parameter ─────────────────────
@medicine_bp.route("/search", methods=["GET"])
def search_medicine():
    """
    Alternative search using query parameter.
    
    URL pattern: /search?q=paracetamol
    Useful for the search bar in the frontend.
    """
    
    query = request.args.get("q", "").strip()
    
    if not query:
        return jsonify({"error": "Please provide a search term. Example: /search?q=aspirin"}), 400
    
    if len(query) < 2:
        return jsonify({"error": "Search term too short. Please enter at least 2 characters."}), 400
    
    # Reuse the same lookup logic
    medicine_name = query.lower()
    
    local_result = fetch_local_medicine(medicine_name)
    if local_result and "error" not in local_result:
        local_result["source"] = "local"
        return jsonify(local_result), 200
    
    api_result = fetch_medicine_info(medicine_name)
    if "error" not in api_result:
        api_result["source"] = "openFDA"
        return jsonify(api_result), 200
    
    return jsonify({
        "error": f"No results found for '{query}'.",
        "suggestion": "Try a different spelling or the generic drug name."
    }), 404


# ── ROUTE 4: List All Local Medicines ────────────────────────
@medicine_bp.route("/medicines/local", methods=["GET"])
def list_local_medicines():
    """
    Returns the list of all medicines available in local database.
    Useful for autocomplete suggestions in the frontend.
    """
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'medicines_local.json')
        with open(data_path, "r") as f:
            local_data = json.load(f)
        
        medicine_list = [
            {"key": key, "name": info["name"]}
            for key, info in local_data.items()
        ]
        
        return jsonify({
            "count": len(medicine_list),
            "medicines": medicine_list
        }), 200
    
    except FileNotFoundError:
        return jsonify({"error": "Local medicine database not found."}), 500
    
    # Add this import at the top of routes.py
from app.voice_assistant import text_to_speech, speak_medicine_info
import os

# ── ROUTE 5: Generate Audio ───────────────────────────────────
@medicine_bp.route("/speak", methods=["POST"])
def speak():
    """
    Accepts medicine info + language, returns audio file path.
    
    POST body (JSON):
    {
        "medicine_info": { ...medicine dict... },
        "language": "English",
        "section": "summary"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    medicine_info = data.get("medicine_info", {})
    language = data.get("language", "English")
    section = data.get("section", "summary")
    
    if not medicine_info:
        return jsonify({"error": "medicine_info is required"}), 400
    
    result = speak_medicine_info(medicine_info, language, section)
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify({"success": True, "message": f"Speaking {section} in {language}"}), 200