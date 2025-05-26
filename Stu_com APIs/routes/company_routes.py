import os
import boto3
from flask import Blueprint, request, jsonify
from utils.auth_utils import hash_password, check_password, generate_jwt

company_bp = Blueprint('company', __name__)
dynamodb = boto3.client('dynamodb', region_name=os.getenv("REGION_NAME", "us-east-1"))
COMPANY_TABLE = os.getenv("COMPANY_TABLE", "Company")

@company_bp.route('/signup/company', methods=['POST'])
def signup_company():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not all([email, name, password]):
        return jsonify({"error": "Missing fields"}), 400

    result = dynamodb.get_item(TableName=COMPANY_TABLE, Key={"email": {"S": email}})
    if 'Item' in result:
        return jsonify({"error": "Company already exists"}), 409

    hashed = hash_password(password)

    dynamodb.put_item(
        TableName=COMPANY_TABLE,
        Item={
            "email": {"S": email},
            "name": {"S": name},
            "password": {"S": hashed}
        }
    )
    return jsonify({"message": "Company registered successfully"}), 201

@company_bp.route('/login/company', methods=['POST'])
def login_company():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing fields"}), 400

    result = dynamodb.get_item(TableName=COMPANY_TABLE, Key={"email": {"S": email}})
    user = result.get('Item')

    if not user or not check_password(password, user['password']['S']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_jwt({"email": email, "role": "company"})
    return jsonify({"token": token}), 200
