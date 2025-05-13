import os
import yaml
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Aurora memory API is running."

@app.route('/memory/retrieve', methods=['POST'])
def retrieve_memory():
    try:
        data = request.get_json()
        tags = data.get("tags", [])
        visible_to = data.get("visible_to", [])

        base_dir = os.path.dirname(os.path.abspath(__file__))
        memory_dir = os.path.join(base_dir, "../memory")
        memory_dir = os.path.normpath(memory_dir)

        memories = []

        for root, _, files in os.walk(memory_dir):
            for file in files:
                if not file.endswith(".yaml"):
                    continue

                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        memory = yaml.safe_load(f)

                    # 型と内容の安全性確認
                    if not isinstance(memory, dict):
                        continue
                    if not isinstance(memory.get("tags", []), list):
                        continue
                    if not isinstance(memory.get("visible_to", []), list):
                        continue

                    if not set(tags).intersection(set(memory.get("tags", []))):
                        continue
                    if not set(visible_to).intersection(set(memory.get("visible_to", []))):
                        continue

                    memories.append(memory)

                except Exception as inner_err:
                    print(f"[WARN] Skipping file due to error: {file} → {inner_err}")
                    continue

        return jsonify({"memories": memories})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
