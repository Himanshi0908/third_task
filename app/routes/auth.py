from flask import Blueprint, request, jsonify, current_app, g
from app.models import User
from app.schemas import UserRegistrationSchema, UserLoginSchema, validate_password_complexity
from app import db, bcrypt
import jwt
import datetime
from marshmallow import ValidationError
from app.middleware import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    schema = UserRegistrationSchema()
    try:
        data = schema.load(data)
        validate_password_complexity(data['password'])
    except ValidationError as err:
        return jsonify(err.messages), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        name=data['name'],
        email=data['email'],
        password_hash=hashed_password,
        role=data.get('role', 'user')
    )
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    schema = UserLoginSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        # Access Token
        access_token_payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15) # 15 mins
        }
        access_token = jwt.encode(access_token_payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

        # Refresh Token
        refresh_token_payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7) # 7 days
        }
        refresh_token = jwt.encode(refresh_token_payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'message': 'Refresh token missing'}), 403

    try:
        # Decode refresh token
        decoded = jwt.decode(refresh_token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded['user_id']
        
        # Verify user still exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 403

        # Issue new access token
        access_token_payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        access_token = jwt.encode(access_token_payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

        return jsonify({'access_token': access_token}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token'}), 401

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    user = g.user
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    # Stateless JWTs don't really support server-side logout without blacklist
    # But we return 200 as requested
    return jsonify({'message': 'Logged out successfully'}), 200
