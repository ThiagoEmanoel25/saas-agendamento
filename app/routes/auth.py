from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import ValidationError
from app.schemas import UserRegisterSchema, UserLoginSchema

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = UserRegisterSchema(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Check if email already exists
    if User.query.filter_by(email=data.email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        email=data.email,
        name=data.name,
        password_hash=generate_password_hash(data.password),
        tenant_id=1,
        role='patient'
    )
    
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "email": user.email,
        "name": user.name
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = UserLoginSchema(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    user = User.query.filter_by(email=data.email).first()
    
    if not user or not check_password_hash(user.password_hash, data.password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "email": user.email,
        "name": user.name
    }), 200
