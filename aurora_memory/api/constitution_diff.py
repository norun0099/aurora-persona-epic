from typing import Any, List
import yaml
import difflib


def load_yaml(filepath: str) -> dict[str, Any]:
    """YAMLファイルを読み込み、辞書として返す。"""
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


if __name__ == "__main__":
    # 仮パス（必要に応じて調整）
    old_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    new_path = "aurora_memory/tmp/proposed_constitution.yaml"
    diff_output = "aurora_memory/tmp/constitution_diff.txt"

    old_yaml = load_yaml(old_path)
    new_yaml = load_yaml(new_path)
    diff = compare_yaml(old_yaml, new_yaml)
    save_diff_report(diff, diff_output)

    print(f"差分が検出されました。内容を {diff_output} に保存しました。")
