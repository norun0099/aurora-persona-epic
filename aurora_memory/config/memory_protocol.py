import yaml
from pathlib import Path

class MemoryProtocol:
    def __init__(self, protocol_path, template_path="aurora_memory/config/structure_template.yaml"):
        self.protocol_path = Path(protocol_path)
        self.template_path = Path(template_path)
        self.protocol = self._load_protocol()
        self.template = self._load_template()

    def _load_protocol(self):
        if not self.protocol_path.exists():
            raise FileNotFoundError(f"Protocol file not found: {self.protocol_path}")
        with open(self.protocol_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_template(self):
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        with open(self.template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def validate_author(self, author):
        persona_namespace = author.lower()
        if persona_namespace not in self._allowed_persona_namespaces():
            print("[Aurora Debug] Author validation failed:", author)
            return False
        return True

    def validate_tags(self, tags, author):
        if not tags or tags[0].lower() != author.lower():
            print("[Aurora Debug] Tags validation failed. First tag:", tags[0] if tags else "None")
            return False
        return True

    def validate_visible_to(self, visible_to):
        allowed_namespaces = self._allowed_persona_namespaces()
        for item in visible_to:
            if item.lower() not in allowed_namespaces:
                print("[Aurora Debug] Visible_to validation failed:", item)
                return False
        return True

    def validate_against_template(self, memory_data: dict):
        """
        記録がテンプレートに完全準拠しているかを厳格に検証。
        すべての必須項目が存在するかどうかを確認する。
        """
        for key in self.template.keys():
            if key not in memory_data:
                print(f"[Aurora Debug] Missing field in memory_data: {key}")
                return False, f"{key} が不足しています"
        return True, "準拠確認OK"

    def _allowed_persona_namespaces(self):
        validation = self.protocol["rules"]["visible_to"]["validation"]
        start = validation.find("(")
        end = validation.find(")")
        if start != -1 and end != -1:
            content = validation[start + 1 : end]
            namespaces = [s.strip().strip("'") for s in content.split(",")]
            return namespaces
        return []

    def debug_protocol(self):
        print("[Aurora Debug] Loaded Protocol:")
        print(yaml.dump(self.protocol, allow_unicode=True, sort_keys=False))

    def debug_template(self):
        print("[Aurora Debug] Loaded Structure Template:")
        print(yaml.dump(self.template, allow_unicode=True, sort_keys=False))
