import os
import json
from typing import List

# 環境変数から設定を取得
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")
GIT_SCAN_ENABLED = os.getenv("GIT_SCAN_ENABLED", "false").lower() == "true"
GIT_SCAN_IGNORE = os.getenv("GIT_SCAN_IGNORE", ".git,__pycache__").split(",")
GIT_SCAN_DEPTH = int(os.getenv("GIT_SCAN_DEPTH", "-1"))

def scan_directory(path: str, depth: int = -1, ignore: List[str] = []) -> dict:
    """
    指定されたディレクトリパスを再帰的にスキャンし、構造を辞書で返す
    """
    result = {}
    try:
        entries = os.listdir(path)
    except Exception as e:
        return {"error": str(e)}

    for entry in entries:
        full_path = os.path.join(path, entry)
        rel_path = os.path.relpath(full_path, GIT_REPO_PATH)

        if any(part in rel_path.split(os.sep) for part in ignore):
            continue

        if os.path.isdir(full_path):
            if depth == 0:
                result[entry] = "<dir>"
            else:
                result[entry] = scan_directory(full_path, depth - 1 if depth > 0 else -1, ignore)
        else:
            result[entry] = "<file>"

    return result

def main():
    if not GIT_SCAN_ENABLED:
        print("[INFO] Git構造スキャンは無効化されています")
        return

    print(f"[INFO] Git構造をスキャン中: {GIT_REPO_PATH} (深度: {GIT_SCAN_DEPTH})")
    structure = scan_directory(GIT_REPO_PATH, GIT_SCAN_DEPTH, GIT_SCAN_IGNORE)
    print(json.dumps(structure, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
