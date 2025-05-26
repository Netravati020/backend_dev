import os
import boto3
from flask import Blueprint, request, jsonify
from utils.auth_utils import hash_password, check_password, generate_jwt

student_bp = Blueprint('student', __name__)
dynamodb = boto3.client('dynamodb', region_name=os.getenv("REGION_NAME", "us-east-1"))
STUDENT_TABLE = os.getenv("STUDENT_TABLE", "Student")

@student_bp.route('/signup/student', methods=['POST'])
def signup_student():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not all([email, name, password]):
        return jsonify({"error": "Missing fields"}), 400

    result = dynamodb.get_item(TableName=STUDENT_TABLE, Key={"email": {"S": email}})
    if 'Item' in result:
        return jsonify({"error": "Student already exists"}), 409

    hashed = hash_password(password)

    dynamodb.put_item(
        TableName=STUDENT_TABLE,
        Item={
            "email": {"S": email},
            "name": {"S": name},
            "password": {"S": hashed}
        }
    )
    return jsonify({"message": "Student registered successfully"}), 201

@student_bp.route('/login/student', methods=['POST'])
def login_student():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing fields"}), 400

    result = dynamodb.get_item(TableName=STUDENT_TABLE, Key={"email": {"S": email}})
    user = result.get('Item')

    if not user or not check_password(password, user['password']['S']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_jwt({"email": email, "role": "student"})
    return jsonify({"token": token}), 200
