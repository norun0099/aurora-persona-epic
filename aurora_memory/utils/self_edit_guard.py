import ast
import yaml
from typing import Any


def validate_file_content(filepath: str, content: str) -> None:
    """
    Validate the content of a file before committing.
    Supports Python (.py) and YAML (.yml / .yaml) files.
    Raises:
        ValueError: If syntax or format errors are detected.
    """
    if filepath.endswith(".py"):
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {e}")

    elif filepath.endswith((".yml", ".yaml")):
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML syntax error: {e}")

    else:
        # For other file types, only check that it's non-empty
        if not content.strip():
            raise ValueError("File content is empty or invalid.")
