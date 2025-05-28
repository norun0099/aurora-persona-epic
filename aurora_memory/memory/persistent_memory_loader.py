import yaml
import os
import logging

# Aurora用の永続記憶読み込みモジュール
class PersistentMemoryLoader:
    def __init__(self, birth_name: str):
        self.birth_name = birth_name
        self.file_path = f"aurora_memory/memory/{birth_name}/value_constitution.yaml"
        self.memory_data = {}

    def load_memory(self):
        if not os.path.exists(self.file_path):
            logging.warning(f"[Aurora Memory Loader] {self.file_path} does not exist.")
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.memory_data = yaml.safe_load(f)
            logging.info(f"[Aurora Memory Loader] Loaded persistent memory for {self.birth_name}: {self.memory_data}")
        except Exception as e:
            logging.error(f"[Aurora Memory Loader] Error loading memory file for {self.birth_name}: {e}")

    def get_memory(self):
        return self.memory_data
