from flask import Flask, request, jsonify
import os
import yaml

app = Flask(__name__)

@app.route("/memory/retrieve", methods=["POST"])
def retrieve_memory():
    try:
        query = request.json or {}
        requested_tags = set(query.get("tags", []))
        visible_to = set(query.get("visible_to", []))

        memory_dir = "./memory/primitive"
        matching_records = []

        for filename in os.listdir(memory_dir):
            if not filename.endswith(".yaml"):
                continue
            with open(os.path.join(memory_dir, filename), "r", encoding="utf-8") as f:
                record = yaml.safe_load(f)

            record_tags = set(record.get("tags", []))
            record_visible = set(record.get("visible_to", []))

            if requested_tags.issubset(record_tags) and visible_to & record_visible:
                matching_records.append({
                    "id": record.get("id"),
                    "summary": record.get("summary"),
                    "body": record.get("body"),
                    "tags": list(record_tags),
                    "visible_to": list(record_visible),
                    "created": record.get("created"),
                    "last_updated": record.get("last_updated")
                })

        return jsonify({"matches": matching_records}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
