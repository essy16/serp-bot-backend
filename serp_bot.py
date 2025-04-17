from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route("/start-bot", methods=["POST"])
def start_bot():
    data = request.json
    keywords = data.get("keywords", [])
    print("✅ Received keywords:", keywords)

    return jsonify({
        "status": "started",
        "keywords": keywords
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)