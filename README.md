# Test Exam Backend - Flask + AWS Lambda + DynamoDB

A serverless backend for an exam platform providing secure sign-up and login APIs for both **Company** and **Student** users. Built using **Flask**, **AWS Lambda**, **DynamoDB**, **JWT**, and **bcrypt**, and deployed using the **Serverless Framework**.

---

##  Features

-  Company & Student Sign Up / Sign In
-  Password hashing with `bcrypt`
-  JWT-based Authentication
-  Serverless deployment with AWS Lambda
-  DynamoDB as database

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
npm install -g serverless
sls deploy
sls offline start
