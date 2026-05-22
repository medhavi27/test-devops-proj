from flask import Flask, jsonify
import time
import os

app = Flask(__name__)

visit_count = 0

@app.route("/")
def home():
    global visit_count
    visit_count += 1
    return f"<h1>Hello from my DevOps app!</h1><p>Visits: {visit_count}</p>"

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})

@app.route("/metrics-test")
def metrics_test():
    return jsonify({"visits": visit_count, "app": "devops-demo"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)