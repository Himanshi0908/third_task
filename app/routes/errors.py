from flask import Blueprint, jsonify

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return jsonify({'message': 'Resource not found'}), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    return jsonify({'message': 'Permission denied'}), 403

@errors_bp.app_errorhandler(401)
def unauthorized_error(error):
    return jsonify({'message': 'Unauthorized'}), 401
