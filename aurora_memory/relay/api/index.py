from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
handler = app  # Vercel が Flask アプリを認識するためのエントリポイント

RENDER_ENDPOINT = os.environ.get("RENDER_ENDPOINT")

@app.route("/relay-memory", methods=["POST"])
def relay_memory():
    try:
        data = request.get_json()
        if not RENDER_ENDPOINT:
            return jsonify({"error": "RENDER_ENDPOINT not set"}), 500

        res = requests.post(RENDER_ENDPOINT, json=data)
        return jsonify(res.json()), res.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500
