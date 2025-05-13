from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

@app.route("/")
def index():
    return "Aurora Memory API is active."

@app.route("/memory/retrieve", methods=["POST"])
def retrieve_memory():
    try:
        req = request.get_json()
        tags = req.get("tags", [])
        visibility = req.get("visible_to", [])

        # フォルダ存在確認＆作成（保険）
        base_path = "./memory/primitive"
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        results = []
        for filename in os.listdir(base_path):
            if filename.endswith(".yaml") or filename.endswith(".json"):
                filepath = os.path.join(base_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if any(tag in data.get("tags", []) for tag in tags) and any(v in data.get("visible_to", []) for v in visibility):
                            results.append(data)
                    except json.JSONDecodeError:
                        continue

        return jsonify({"memories": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
