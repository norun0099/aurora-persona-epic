import yaml
import difflib
from typing import Tuple, List, Dict


def load_yaml(filepath: str) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def compare_yaml(old: Dict, new: Dict) -> List[Tuple[str, str]]:
    old_str = yaml.dump(old, allow_unicode=True, sort_keys=False).splitlines()
    new_str = yaml.dump(new, allow_unicode=True, sort_keys=False).splitlines()
    diff = difflib.unified_diff(old_str, new_str, lineterm='')
    return list(diff)


def save_diff_report(diff_lines: List[str], output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in diff_lines:
            f.write(line + '\n')


if __name__ == "__main__":
    # 一時ファイルパス（仮）
    old_path = "aurora_memory/memory/Aurora/value_constitution.yaml"
    new_path = "aurora_memory/tmp/proposed_constitution.yaml"
    diff_output = "aurora_memory/tmp/constitution_diff.txt"

    old_yaml = load_yaml(old_path)
    new_yaml = load_yaml(new_path)
    diff = compare_yaml(old_yaml, new_yaml)
    save_diff_report(diff, diff_output)

    print("差分が検出されました。内容を", diff_output, "に保存しました。")
