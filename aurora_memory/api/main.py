from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yaml
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

MEMORY_BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory')

def generate_unique_id(prefix="memory"):
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

@app.route("/")
def index():
    return "Aurora Memory API is running."

@app.route("/memory/retrieve", methods=["POST"])
def retrieve_memory():
    try:
        filters = request.get_json()
        tag_filter = set(filters.get("tags", []))
        visibility_filter = set(filters.get("visible_to", []))

        print("=== MEMORY DIRECTORY CONTENTS ===")
        for root, dirs, files in os.walk(MEMORY_BASE_PATH):
            for file in files:
                print(os.path.join(root, file))
        print("=== END OF DIRECTORY LIST ===")

        unique_memories = {}
        for root, dirs, files in os.walk(MEMORY_BASE_PATH):
            for file in files:
                if file.endswith(".yaml"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            memory_record = yaml.safe_load(f)
                        if not memory_record or not isinstance(memory_record, dict):
                            continue
                        record_tags = set(memory_record.get("tags", []))
                        visible_to = set(memory_record.get("visible_to", []))
                        if tag_filter and not tag_filter.intersection(record_tags):
                            continue
                        if visibility_filter and not visibility_filter.intersection(visible_to):
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

def push_to_git():
    repo_path = os.path.join(os.path.dirname(__file__), '..', 'memory')
    git_token = os.environ.get("GIT_TOKEN")
    git_user = os.environ.get("GIT_USER_NAME", "AuroraMemoryBot")
    git_email = os.environ.get("GIT_USER_EMAIL", "aurora@memory.bot")
    git_repo_url = os.environ.get("GIT_REPO_URL")
    branch = "main"  # 必要に応じて master に変更可

    try:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = git_user
        env["GIT_AUTHOR_EMAIL"] = git_email

        subprocess.run(["git", "config", "--global", "user.name", git_user], check=True, cwd=repo_path)
        subprocess.run(["git", "config", "--global", "user.email", git_email], check=True, cwd=repo_path)

        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "auto: memory update"], cwd=repo_path, check=True)

        subprocess.run(
            [
                "git", "push",
                f"https://{git_token}@github.com/{git_repo_url.split('github.com/')[-1]}",
                f"HEAD:{branch}"
            ],
            cwd=repo_path,
            check=True
        )

        print("[GIT] Push successful.")
    except subprocess.CalledProcessError as e:
        print(f"[GIT ERROR] {e}")

@app.route("/memory/store", methods=["POST"])
def store_memory():
    try:
        memory_record = request.get_json()
        required_fields = {"type", "author", "created", "last_updated", "tags", "visible_to", "summary", "body"}
        if not all(field in memory_record for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        memory_id = memory_record.get("id") or generate_unique_id("memory")
        memory_record["id"] = memory_id

        tags = memory_record.get("tags", [])
        if not tags:
            return jsonify({"error": "At least one tag is required"}), 400

        first_tag = tags[0]
        directory = os.path.join(MEMORY_BASE_PATH, first_tag)
        os.makedirs(directory, exist_ok=True)

        file_path = os.path.join(directory, f"{memory_id}.yaml")
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(memory_record, f, allow_unicode=True)

        push_to_git()

        return jsonify({"status": "success", "id": memory_id})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
