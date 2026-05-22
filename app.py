# app.py
from flask import Flask
from database import init_db
from routes import api

app = Flask(__name__)

# 2. Register our routes Blueprint with the main Flask app
app.register_blueprint(api)

if __name__ == "__main__":
    # 1. Fire up the database connection loop & table schemas
    init_db()
    app.run(host="0.0.0.0", port=5000)