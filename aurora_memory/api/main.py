from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yaml
import subprocess
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

MEMORY_BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory')

def generate_unique_id(prefix="memory"):
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

def sanitize_tag(tag):
    # フォルダ名として安全なタグか確認（英数字・アンダーバーのみ許可）
    return re.match(r'^[\w-]+$', tag)

@app.route("/")
def index():
    return "Aurora Memory API is running."

@app.route("/memory/retrieve", methods=["POST"])
def retrieve_memory():
    try:
        filters = request.get_json()
        tag_filter = set(filters.get("tags", []))
        visibility_filter = set(filters.get("visible_to", []))

        unique_memories = {}
        for root, _, files in os.walk(MEMORY_BASE_PATH):
            for file in files:
                if file.endswith(".yaml"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            memory_record = yaml.safe_load(f)
                        if not isinstance(memory_record, dict):
                            continue
                        record_tags = set(memory_record.get("tags", []))
                        visible_to = set(memory_record.get("visible_to", []))
                        if tag_filter and not tag_filter & record_tags:
                            continue
                        if visibility_filter and not visibility_filter & visible_to:
                            continue
                        record_id = memory_record.get("id")
                        if record_id:
                            unique_memories[record_id] = memory_record
                    except Exception as inner_e:
                        print(f"[YAML LOAD ERROR] {file_path}: {inner_e}")

        return jsonify({"memories": list(unique_memories.values())})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/memory/store", methods=["POST"])
def store_memory():
    try:
        memory_record = request.get_json()
        required_fields = {"type", "author", "created", "last_updated", "tags", "visible_to", "summary", "body"}
        if not all(field in memory_record for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        tags = memory_record.get("tags", [])
        if not tags or not sanitize_tag(tags[0]):
            return jsonify({"error": "Invalid or missing first tag"}), 400

        visible_to = memory_record.get("visible_to", [])
        if "aurora" not in visible_to:
            return jsonify({"error": "Missing visibility to 'aurora'"}), 403

        memory_id = memory_record.get("id") or generate_unique_id("memory")
        memory_record["id"] = memory_id

        directory = os.path.join(MEMORY_BASE_PATH, tags[0])
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{memory_id}.yaml")
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(memory_record, f, allow_unicode=True)

        git_token = os.environ.get("GIT_TOKEN")
        git_url = os.environ.get("GIT_REPO_URL")

        subprocess.run(["git", "add", "."], cwd=os.path.join(os.path.dirname(__file__), '..'), check=True)
        subprocess.run(["git", "commit", "-m", "auto: memory update"], cwd=os.path.join(os.path.dirname(__file__), '..'), check=True)
        subprocess.run([
            "git", "push", f"https://{git_token}@{git_url.split('https://')[-1]}"
        ], cwd=os.path.join(os.path.dirname(__file__), '..'), check=True)

        return jsonify({"status": "success", "id": memory_id})

    except subprocess.CalledProcessError as git_err:
        print(f"[GIT ERROR] {git_err}")
        return jsonify({"error": "Git commit or push failed"}), 500

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
