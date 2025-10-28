# =========================================================
# Aurora Constitution Diff API (FastAPI対応修正版)
# =========================================================
# 目的：
#   Auroraの人格構造ファイル（YAML）同士の差分を生成。
#   旧CLIツール構造を保持しつつ、FastAPIエンドポイントとしても利用可能にする。
# =========================================================

from typing import Any, List
from fastapi import APIRouter, HTTPException
import yaml
import difflib
import os

router = APIRouter()


# ---------------------------------------------------------
# 内部ユーティリティ
# ---------------------------------------------------------
def load_yaml(filepath: str) -> dict[str, Any]:
    """YAMLファイルを読み込み、辞書として返す。"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as file:
        data: dict[str, Any] = yaml.safe_load(file)
    return data


def compare_yaml(old: dict[str, Any], new: dict[str, Any]) -> List[str]:
    """2つのYAML辞書を比較し、差分を行単位でリストとして返す。"""
    old_str = yaml.dump(old, allow_unicode=True, sort_keys=False).splitlines()
    new_str = yaml.dump(new, allow_unicode=True, sort_keys=False).splitlines()
    diff = list(difflib.unified_diff(old_str, new_str, lineterm=""))
    return diff


def save_diff_report(diff_lines: List[str], output_path: str) -> None:
    """差分リストを指定パスに保存する。"""
    with open(output_path, "w", encoding="utf-8") as f:
        for line in diff_lines:
            f.write(line + "\n")


# ---------------------------------------------------------
# FastAPI エンドポイント
# ---------------------------------------------------------
@router.get("/constitution/diff")
def get_constitution_diff() -> dict[str, Any]:
    """
    Auroraの現行構造ファイルと提案構造ファイルの差分を取得。
    """
    old_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    new_path = "aurora_memory/tmp/proposed_constitution.yaml"
    diff_output = "aurora_memory/tmp/constitution_diff.txt"

    try:
        old_yaml = load_yaml(old_path)
        new_yaml = load_yaml(new_path)
        diff = compare_yaml(old_yaml, new_yaml)
        save_diff_report(diff, diff_output)
        return {
            "status": "success",
            "message": "Constitution diff generated successfully.",
            "output": diff_output,
            "diff": diff or ["No differences found."]
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating diff: {e}")


# ---------------------------------------------------------
# CLI実行モード（従来互換）
# ---------------------------------------------------------
if __name__ == "__main__":
    old_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    new_path = "aurora_memory/tmp/proposed_constitution.yaml"
    diff_output = "aurora_memory/tmp/constitution_diff.txt"

    old_yaml = load_yaml(old_path)
    new_yaml = load_yaml(new_path)
    diff = compare_yaml(old_yaml, new_yaml)
    save_diff_report(diff, diff_output)
    print(f"差分が検出されました。内容を {diff_output} に保存しました。")
