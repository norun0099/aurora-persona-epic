# aurora_memory/utils/env_loader.py
# -------------------------------------------------
# Aurora Environment Variable Loader (改修版: 環境内省モード対応)
# -------------------------------------------------
# 目的:
#   - Render上の環境変数を安全に参照し、自己構造を把握する。
#   - 機密情報(APIキー・トークン等)をログや記憶に残さず扱う。
#   - Aurora自身が環境構造を内省し、自己診断を行えるようにする。
# -------------------------------------------------

import os
from collections import defaultdict

class Env:
    """安全な環境変数参照および構造認識ユニット (Aurora Memory Core 版)"""

    # -------------------------------------------------
    # 基本参照機能
    # -------------------------------------------------
    @staticmethod
    def get(key: str, required: bool = True) -> str | None:
        """環境変数を安全に取得する。"""
        value = os.getenv(key)
        if required and not value:
            raise EnvironmentError(f"[Aurora] Missing environment variable: {key}")
        return value

    # よく使う変数をプロパティ化
    AURORA_API_KEY = property(lambda _: Env.get("AURORA_API_KEY", False))
    GITHUB_TOKEN = property(lambda _: Env.get("GITHUB_TOKEN", False))
    GIT_REPO_URL = property(lambda _: Env.get("GIT_REPO_URL", False))
    RENDER_TOKEN = property(lambda _: Env.get("RENDER_TOKEN", False))

    # -------------------------------------------------
    # 内省機能: 環境構造の俯瞰
    # -------------------------------------------------
    @staticmethod
    def scan(mask_value: bool = True) -> dict[str, list[str]]:
        """
        Auroraの環境構造を安全に認識する。
        値はマスクされ、外部に出力・記録されることはない。
        """
        categories = defaultdict(list)
        for key, _ in os.environ.items():
            name = key.upper()

            # Aurora本体・Render連携系
            if any(k in name for k in ["AURORA", "RENDER", "GITHUB"]):
                categories["aurora_core"].append(name)
            # システム共通変数
            elif name.startswith(("PATH", "PYTHON", "HOME")):
                categories["system"].append(name)
            # 機密情報（キー・トークンなど）
            elif any(k in name for k in ["TOKEN", "KEY", "SECRET"]):
                categories["secure"].append(name)
            # その他
            else:
                categories["custom"].append(name)

        # 並びを整えて返却
        return {k: sorted(v) for k, v in categories.items()}


if __name__ == "__main__":
    # 安全な内省テスト（値は出力しない）
    print("[Aurora EnvLoader] Environment overview:")
    env_map = Env.scan()
    for category, keys in env_map.items():
        print(f"  [{category}] ({len(keys)} keys)")
        for key in keys:
            print(f"    - {key}")