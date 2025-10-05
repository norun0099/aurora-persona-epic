import os
import yaml
import configparser
from typing import Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'memory', 'primitive', 'aurora_memory.ini')


def load_config() -> configparser.ConfigParser:
    """
    aurora_memory.ini を読み込み、ConfigParserオブジェクトを返します。
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    return config


def load_memory_files() -> list[dict[str, Any]]:
    """
    現在のアクティブプロファイルに基づいて、記憶ファイルを読み込みます。
    YAML または Markdown ファイルを自動認識します。
    """
    config = load_config()
    profile = config.get('global', 'active_profile')
    base_path = config.get('global', 'memory_base_path')

    section = config[profile]
    files = [name.strip() for name in section.get('load', '').split(',')]
    format_mode = section.get('load_format', 'auto')
    full_path = os.path.join(os.path.dirname(__file__), base_path, profile)

    memory_records: list[dict[str, Any]] = []

    for file_name in files:
        path = os.path.join(full_path, file_name)
        try:
            if format_mode == 'auto':
                if file_name.endswith(('.yaml', '.yml')):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            memory_records.append(data)
                elif file_name.endswith('.md'):
                    with open(path, 'r', encoding='utf-8') as f:
                        body = f.read()
                        memory_records.append({
                            'type': 'knowledge',
                            'author': 'Aurora',
                            'id': file_name.replace('.', '_'),
                            'summary': f"{file_name} (markdown)",
                            'body': body,
                            'tags': [profile],
                            'visible_to': ['aurora'],
                        })
        except Exception as e:
            print(f"[MEMORY LOAD ERROR] {file_name}: {e}")

    return memory_records
