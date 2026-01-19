from flask import Blueprint, request, jsonify
from app.models import User
from app.schemas import UserRegistrationSchema
from app import db
from app.middleware import token_required, role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_all_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at
        })
    return jsonify(result), 200

@admin_bp.route('/users/<int:id>/role', methods=['PATCH'])
@token_required
@role_required(['admin'])
def update_user_role(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    new_role = data.get('role')
    if new_role not in ['user', 'admin']:
        return jsonify({'message': 'Invalid role. Must be "user" or "admin".'}), 400
        
    user.role = new_role
    db.session.commit()
    
    return jsonify({'message': f'User role updated to {new_role}'}), 200

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200
