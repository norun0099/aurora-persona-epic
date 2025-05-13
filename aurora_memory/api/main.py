from flask import Flask, request, jsonify
import os
import yaml

app = Flask(__name__)

MEMORY_DIR = "./aurora_memory/memory"

# デバッグ用: メモリディレクトリの内容をログ出力
print("=== MEMORY DIRECTORY CONTENTS ===")
for root, dirs, files in os.walk(MEMORY_DIR):
    for file in files:
        print(os.path.join(root, file))
print("=== END OF DIRECTORY LIST ===")


def load_memories():
    memories = []
    for root, _, files in os.walk(MEMORY_DIR):
        for filename in files:
            if filename.endswith(".yaml"):
                path = os.path.join(root, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        memory = yaml.safe_load(f)
                        if memory:
                            memories.append(memory)
                except Exception as e:
                    print(f"[ERROR] Failed to load {filename}: {e}")
    return memories


@app.route("/", methods=["GET"])
def index():
    return "Aurora Memory API is running."


@app.route("/memory/retrieve", methods=["POST"])
def retrieve_memory():
    try:
        data = request.get_json()
        tags = set(data.get("tags", []))
        visible_to = set(data.get("visible_to", []))

        matched = []
        for mem in load_memories():
            if (
                tags.intersection(set(mem.get("tags", []))) and
                visible_to.intersection(set(mem.get("visible_to", [])))
            ):
                matched.append(mem)

        return jsonify({"memories": matched}), 200

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
