import os
import uuid
import boto3
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.auth_utils import generate_jwt

student_bp = Blueprint('student', __name__)
dynamodb = boto3.client('dynamodb', region_name=os.getenv("REGION_NAME", "us-east-1"))
STUDENT_TABLE = os.getenv("STUDENT_TABLE", "Student")

@student_bp.route('/signup/student', methods=['POST'])
def signup_student():
    data = request.get_json()

    required_fields = [
        "first_name", "last_name", "gender", "dob", "address", "postcode", "contact_phone",
        "email", "document", "school_name", "school_percentage", "class",
        "college_name", "college_percentage", "course",
        "criteria_10th", "criteria_12th", "criteria_graduate"
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Validate DOB format (expecting DD-MM-YYYY)
    try:
        dob_obj = datetime.strptime(data["dob"], "%d-%m-%Y")
        dob_iso = dob_obj.strftime("%Y-%m-%d")  # Store in ISO format
    except ValueError:
        return jsonify({"error": "DOB must be in DD-MM-YYYY format"}), 400

    # Generate unique student ID
    student_id = str(uuid.uuid4())[:8]

    # Check uniqueness (in rare conflict)
    existing = dynamodb.get_item(
        TableName=STUDENT_TABLE,
        Key={"student_id": {"S": student_id}}
    )
    if "Item" in existing:
        return jsonify({"error": "Student ID conflict, try again"}), 409

    # Build the student item
    item = {
        "student_id": {"S": student_id},
        "email": {"S": data["email"]},
        "first_name": {"S": data["first_name"]},
        "last_name": {"S": data["last_name"]},
        "gender": {"S": data["gender"]},
        "dob": {"S": dob_iso},
        "address": {"S": data["address"]},
        "postcode": {"S": data["postcode"]},
        "contact_phone": {"S": data["contact_phone"]},
        "document": {"S": data["document"]},
        "school_name": {"S": data["school_name"]},
        "school_percentage": {"S": str(data["school_percentage"])},
        "class": {"S": data["school_class"]},
        "college_name": {"S": data["college_name"]},
        "college_percentage": {"S": str(data["college_percentage"])},
        "course": {"S": data["course"]},
        "criteria_10th": {"BOOL": bool(data["criteria_10th"])},
        "criteria_12th": {"BOOL": bool(data["criteria_12th"])},
        "criteria_graduate": {"BOOL": bool(data["criteria_graduate"])}
    }

    dynamodb.put_item(TableName=STUDENT_TABLE, Item=item)

    return jsonify({
        "message": "Student registered successfully",
        "student_id": student_id,
        "default_password": data["dob"]  # Expected format
    }), 201


@student_bp.route('/login', methods=['POST'])
def student_login():
    data = request.get_json()
    student_id = data.get("student_id")
    password = data.get("password")  # Expecting DD-MM-YYYY format

    if not student_id or not password:
        return jsonify({"error": "Student ID and password required"}), 400

    try:
        result = dynamodb.get_item(
            TableName=STUDENT_TABLE,
            Key={"student_id": {"S": student_id}}
        )
        student = result.get("Item")
        if not student:
            return jsonify({"error": "Student not found"}), 404

        # Validate DOB as password
        stored_dob = datetime.strptime(student["dob"]["S"], "%Y-%m-%d").strftime("%d-%m-%Y")
        if stored_dob != password:
            return jsonify({"error": "Invalid credentials"}), 401

        token = generate_jwt({"student_id": student_id, "role": "student"})
        return jsonify({
            "message": "Login successful",
            "token": token,
            "student_id": student_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

