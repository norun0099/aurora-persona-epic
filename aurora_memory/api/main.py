from flask import Flask, request, jsonify
import os
import yaml

app = Flask(__name__)

@app.route("/memory/retrieve", methods=["POST"])
def retrieve_memory():
    try:
        filters = request.get_json()
        tags = filters.get("tags", [])
        visible_to = filters.get("visible_to", [])

        matched_records = []

        memory_dir = os.path.join(".", "memory", "primitive")
        for filename in os.listdir(memory_dir):
            if filename.endswith(".yaml"):
                filepath = os.path.join(memory_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        record = yaml.safe_load(f)
                        if (
                            any(tag in record.get("tags", []) for tag in tags)
                            and any(v in record.get("visible_to", []) for v in visible_to)
                        ):
                            matched_records.append(record)
                    except Exception as e:
                        print(f"[!] YAML読み込み失敗: {filename} -> {e}")

        return jsonify({"records": matched_records})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] サーバー側例外発生: {e}")
    return jsonify({"error": str(e)}), 500
