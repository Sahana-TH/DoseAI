# routes.py
# All Flask API endpoints for DoseAI

from flask import Blueprint, jsonify, request, send_file
from app.medicine_lookup import fetch_medicine_info, fetch_local_medicine
import json
import os

medicine_bp = Blueprint("medicine", __name__)


# ── ROUTE 1: Health Check ─────────────────────────────────────
@medicine_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "running",
        "message": "DoseAI Backend is live 🚀",
        "version": "2.0.0"
    })


# ── ROUTE 2: Medicine Lookup ──────────────────────────────────
@medicine_bp.route("/medicine/<string:name>", methods=["GET"])
def get_medicine(name):
    medicine_name = name.lower().strip()

    # Try local database first
    local_result = fetch_local_medicine(medicine_name)
    if local_result and "error" not in local_result:
        local_result["source"] = "local"
        return jsonify(local_result), 200

    # Try OpenFDA API
    api_result = fetch_medicine_info(medicine_name)
    if "error" not in api_result:
        api_result["source"] = "openFDA"
        return jsonify(api_result), 200

    return jsonify({
        "error": f"Medicine '{name}' not found.",
        "suggestion": "Check spelling or try the generic name."
    }), 404


# ── ROUTE 3: List Local Medicines ────────────────────────────
@medicine_bp.route("/medicines/local", methods=["GET"])
def list_local_medicines():
    try:
        data_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'medicines_local.json'
        )
        with open(data_path, "r") as f:
            local_data = json.load(f)

        medicine_list = [
            {"key": key, "name": info["name"]}
            for key, info in local_data.items()
        ]
        return jsonify({"count": len(medicine_list), "medicines": medicine_list}), 200

    except FileNotFoundError:
        return jsonify({"error": "Local medicine database not found."}), 500


# ── ROUTE 4: Voice / Speak ────────────────────────────────────
@medicine_bp.route("/speak", methods=["POST"])
def speak():
    """
    Accepts medicine info + language + section.
    Translates text, generates MP3, returns audio bytes.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    medicine_info = data.get("medicine_info", {})
    language      = data.get("language", "English")
    section       = data.get("section", "summary")

    if not medicine_info:
        return jsonify({"error": "medicine_info is required"}), 400

    name = medicine_info.get("name", "this medicine")

    # Build text based on requested section
    if section == "summary":
        text = f"{name}. {medicine_info.get('usage', 'Not available')[:300]}"
    elif section == "dosage":
        text = f"Dosage for {name}: {medicine_info.get('dosage', 'Not available')[:300]}"
    elif section == "side_effects":
        text = f"Side effects of {name}: {medicine_info.get('side_effects', 'Not available')[:300]}"
    elif section == "overdose":
        text = f"Overdose risk for {name}: {medicine_info.get('overdose', 'Not available')[:300]}"
    elif section == "warnings":
        text = f"Warning for {name}: {medicine_info.get('warnings', 'Not available')[:300]}"
    elif section == "full":
        text = (
            f"{name}. "
            f"Usage: {medicine_info.get('usage', '')[:150]}. "
            f"Dosage: {medicine_info.get('dosage', '')[:150]}. "
            f"Side effects: {medicine_info.get('side_effects', '')[:100]}."
        )
    else:
        return jsonify({"error": f"Unknown section '{section}'"}), 400

    # Generate audio (with translation)
    from app.voice_assistant import text_to_speech
    result = text_to_speech(text, language)

    if "error" in result:
        return jsonify(result), 500

    filepath = result.get("filepath")
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Audio file was not created."}), 500

    # Return MP3 file directly as bytes
    return send_file(filepath, mimetype="audio/mpeg", as_attachment=False)


# ── ROUTE 5: OCR Scan ─────────────────────────────────────────
# ── ROUTE 5: OCR Scan ─────────────────────────────────────────
@medicine_bp.route("/scan", methods=["POST"])
def scan_medicine_image():
    """
    Accepts image from either:
    - File upload (multipart form-data with key 'image')
    - Raw bytes (content-type: image/jpeg or image/png)

    Returns:
        JSON: {"raw_text": "...", "medicine_candidates": [...]}
    """
    from PIL import Image
    from app.scanner import extract_text_from_image
    import io

    try:
        # ── Method 1: File upload (multipart/form-data) ───────
        if request.files and "image" in request.files:
            file = request.files["image"]
            if file.filename == "":
                return jsonify({"error": "Empty filename."}), 400

            image_bytes = file.read()
            pil_image   = Image.open(io.BytesIO(image_bytes))

        # ── Method 2: Raw bytes (from st.camera_input) ───────
        elif request.data and len(request.data) > 0:
            pil_image = Image.open(io.BytesIO(request.data))

        # ── Method 3: JSON with base64 image ─────────────────
        elif request.is_json:
            import base64
            data       = request.get_json()
            img_base64 = data.get("image_base64", "")
            if not img_base64:
                return jsonify({"error": "No image data in JSON."}), 400
            img_bytes = base64.b64decode(img_base64)
            pil_image = Image.open(io.BytesIO(img_bytes))

        else:
            return jsonify({"error": "No image provided. Send as form-data, raw bytes, or base64 JSON."}), 400

        # Run OCR
        result = extract_text_from_image(pil_image)

        if "error" in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500
    # ── ROUTE 6: Debug Tesseract ──────────────────────────────────
@medicine_bp.route("/debug/tesseract", methods=["GET"])
def debug_tesseract():
    import subprocess
    import sys

    results = {
        "platform": sys.platform,
        "paths": {},
        "which": None,
        "version": None
    }

    for path in [
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
        "/opt/render/project/.apt/usr/bin/tesseract"
    ]:
        results["paths"][path] = os.path.exists(path)

    try:
        r = subprocess.run(
            ["which", "tesseract"],
            capture_output=True, text=True, timeout=5
        )
        results["which"] = r.stdout.strip() or "not found"
    except Exception as e:
        results["which"] = str(e)

    try:
        r = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True, text=True, timeout=5
        )
        results["version"] = r.stdout[:100] or r.stderr[:100]
    except Exception as e:
        results["version"] = str(e)

    return jsonify(results)