import os
import ast
import yaml


def validate_file_content(filepath: str, content: str):
    """
    Validate the content of a file before committing.
    Supports Python and YAML for now.
    """
    if filepath.endswith(".py"):
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {e}")

    elif filepath.endswith(".yml") or filepath.endswith(".yaml"):
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML syntax error: {e}")

    else:
        # For other file types, only check that it's non-empty
        if not content.strip():
            raise ValueError("File content is empty or invalid.")

    return True
