import os
import boto3
from flask import Blueprint, request, jsonify
from utils.auth_utils import hash_password, check_password, generate_jwt
from datetime import datetime

student_bp = Blueprint('student', __name__)
dynamodb = boto3.client('dynamodb', region_name=os.getenv("REGION_NAME", "us-east-1"))
STUDENT_TABLE = os.getenv("STUDENT_TABLE", "Student")


@student_bp.route('/signup/student', methods=['POST'])
def signup_student():
    data = request.get_json()

    required_fields = [
        "first_name", "last_name", "gender", "dob", "address", "postcode", "contact_phone",
        "email", "document", "school_name", "school_percentage", "school_class",
        "college_name", "college_percentage", "course", "class_10th_percentage",
        "class_12th_percentage", "graduate"
    ]

    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    email = data["email"]
    result = dynamodb.get_item(TableName=STUDENT_TABLE, Key={"email": {"S": email}})
    if 'Item' in result:
        return jsonify({"error": "Student already exists"}), 409
    # Validate DOB format
    try:
        datetime.strptime(data["dob"], "%d-%m-%Y")
    except ValueError:
        return jsonify({"error": "DOB must be in DD-MM-YYYY format"}), 400

    hashed_password = hash_password(data['password'])

    item = {
        "email": {"S": email},
        "first_name": {"S": data["first_name"]},
        "last_name": {"S": data["last_name"]},
        "gender": {"S": data["gender"]},
        "dob": {"S": data["dob"]},
        "address": {"S": data["address"]},
        "postcode": {"S": data["postcode"]},
        "contact_phone": {"S": data["contact_phone"]},
        "document": {"S": data["document"]},
        "school_name": {"S": data["school_name"]},
        "school_percentage": {"S": str(data["school_percentage"])},
        "school_class": {"S": data["school_class"]},
        "college_name": {"S": data["college_name"]},
        "college_percentage": {"S": str(data["college_percentage"])},
        "course": {"S": data["course"]},
        "class_10th_percentage": {"BOOL": bool(data["criteria_10th"])},
        "class_12th_percentage": {"BOOL": bool(data["criteria_12th"])},
        "graduate": {"BOOL": bool(data["criteria_graduate"])},
    }

    dynamodb.put_item(TableName=STUDENT_TABLE, Item=item)

    return jsonify({"message": "Student registered successfully"}), 201

@student_bp.route('/login/student', methods=['POST'])
def student_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    dynamodb = boto3.client('dynamodb', region_name=os.getenv("REGION_NAME", "us-east-1"))
    STUDENT_TABLE = os.getenv("STUDENT_TABLE", "Student")

    result = dynamodb.get_item(TableName=STUDENT_TABLE, Key={"email": {"S": email}})
    student = result.get("Item")

    if not student:
        return jsonify({"error": "Invalid credentials"}), 401

    stored_hashed_password = student["password"]["S"]

    if not check_password(password, stored_hashed_password):
        return jsonify({"error": "Invalid credentials"}), 401

    token_payload = {
        "email": email,
        "role": "student"
    }
    token = generate_jwt(token_payload)

    return jsonify({"message": "Login successful", "token": token}), 200
