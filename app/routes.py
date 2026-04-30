# filepath: app/routes.py
from flask import Blueprint, request, jsonify
from app.medicine_lookup import get_medicine_info

api = Blueprint('api', __name__)

@api.route('/medicine/<name>', methods=['GET'])
def medicine_lookup(name):
    """API endpoint to look up medicine information."""
    result = get_medicine_info(name)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Medicine not found'}), 404

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})