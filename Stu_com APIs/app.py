from flask import Flask
from routes.company_routes import company_bp
from routes.student_routes import student_bp

app = Flask(__name__)

app.register_blueprint(company_bp)
app.register_blueprint(student_bp)

@app.route('/ping')
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    app.run(debug=True)
