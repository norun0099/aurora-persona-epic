from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yaml
import subprocess
from datetime import datetime
from typing import Dict

# 静的記憶のロード
from aurora_memory import load_memory_files

app = Flask(__name__)
CORS(app)

MEMORY_BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory')
ALLOWED_NAMESPACES = {
    "primitive", "relation", "emotion", "music",
    "request", "technology", "salon", "veil", "desire"
}

STATIC_KNOWLEDGE = load_memory_files()  # ← ここで静的記憶を読み込み

def generate_unique_id(prefix="memory"):
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

def evaluate_memory_quality(memory: Dict[str, str]) -> bool:
    summary = memory.get("summary", "")
    body = memory.get("body", "")

    def score_length(text: str, ideal: int = 100) -> float:
        length = len(text.strip())
        return min(length / ideal, 1.0)

    summary_score = score_length(summary)
    body_score = score_length(body, ideal=200)
    average_score = (summary_score + body_score) / 2

    if average_score >= 0.75:
        return True
    if summary_score >= 0.8 or body_score >= 0.8:
        return True
    return False

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

        # 動的記憶から取得
        for root, _, files in os.walk(MEMORY_BASE_PATH):
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

        # 静的記憶（STATIC_KNOWLEDGE）からも検索
        for mem in STATIC_KNOWLEDGE:
            record_tags = set(mem.get("tags", []))
            visible_to = set(mem.get("visible_to", []))
            if tag_filter and not tag_filter.intersection(record_tags):
                continue
            if visibility_filter and not visibility_filter.intersection(visible_to):
                continue
            record_id = mem.get("id")
            if record_id:
                unique_memories[record_id] = mem

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

        if not evaluate_memory_quality(memory_record):
            return jsonify({"status": "rejected", "reason": "insufficient memory quality"}), 400

        memory_id = memory_record.get("id") or generate_unique_id("memory")
        memory_record["id"] = memory_id

        tags = memory_record.get("tags", [])
        if not tags:
            return jsonify({"error": "At least one tag is required"}), 400

        first_tag = next((tag for tag in tags if tag in ALLOWED_NAMESPACES), "primitive")
        if first_tag != tags[0]:
            print(f"[WARNING] Invalid first tag '{tags[0]}', using fallback 'primitive'")
        memory_record["tags"] = list({first_tag} | set(tags))

        raw_visible_to = memory_record.get("visible_to", [])
        filtered_visible_to = [v for v in raw_visible_to if v in ALLOWED_NAMESPACES]
        memory_record["visible_to"] = filtered_visible_to

        directory = os.path.join(MEMORY_BASE_PATH, first_tag)
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{memory_id}.yaml")
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(memory_record, f, allow_unicode=True)

        subprocess.run(["git", "config", "user.name", memory_record.get("author", "AuroraMemoryBot")], check=True)
        subprocess.run(["git", "config", "user.email", "aurora@memory.bot"], check=True)
        subprocess.run(["git", "add", "."], cwd=os.path.join(os.path.dirname(__file__), ".."), check=True)
        subprocess.run(["git", "commit", "-m", "auto: memory update"], cwd=os.path.join(os.path.dirname(__file__), ".."), check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=os.path.join(os.path.dirname(__file__), ".."), check=True)

        print(f"[GIT] Push successful.")
        return jsonify({"status": "success", "id": memory_id})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
