import yaml
from pathlib import Path

class MemoryProtocol:
    def __init__(self, protocol_path):
        self.protocol_path = Path(protocol_path)
        self.protocol = self._load_protocol()

    def _load_protocol(self):
        if not self.protocol_path.exists():
            raise FileNotFoundError(f"Protocol file not found: {self.protocol_path}")
        with open(self.protocol_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def validate_author(self, author):
        """
        authorが必ずバース名（例えば 'technology', 'primitive' など）であるかを確認する。
        """
        persona_namespace = author.lower()
        # バリデーション：author は必ず persona_namespace に合致する
        if persona_namespace not in self._allowed_persona_namespaces():
            print("[Aurora Debug] Author validation failed:", author)
            return False
        return True

    def validate_tags(self, tags, author):
        """
        tagsの先頭が必ずauthor名（バース名）であることを確認する。
        """
        if not tags or tags[0].lower() != author.lower():
            print("[Aurora Debug] Tags validation failed. First tag:", tags[0] if tags else "None")
            return False
        return True

    def validate_visible_to(self, visible_to):
        """
        visible_to の各要素が許可された persona namespace に属するか確認する。
        """
        allowed_namespaces = self._allowed_persona_namespaces()
        for item in visible_to:
            if item.lower() not in allowed_namespaces:
                print("[Aurora Debug] Visible_to validation failed:", item)
                return False
        return True

    def _allowed_persona_namespaces(self):
        """
        プロトコルから許可された persona namespace を抽出。
        （例: technology, primitive, emotion など）
        """
        # visible_to の validation ルールから取得
        validation = self.protocol["rules"]["visible_to"]["validation"]
        start = validation.find("(")
        end = validation.find(")")
        if start != -1 and end != -1:
            content = validation[start + 1 : end]
            # 例: ('technology', 'primitive')
            namespaces = [s.strip().strip("'") for s in content.split(",")]
            return namespaces
        return []

    def debug_protocol(self):
        """
        読み込んだプロトコル内容を表示するデバッグメソッド。
        """
        print("[Aurora Debug] Loaded Protocol:")
        print(yaml.dump(self.protocol, allow_unicode=True, sort_keys=False))
