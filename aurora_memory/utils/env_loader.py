# aurora_memory/utils/env_loader.py
# -------------------------------------------------
# Aurora Environment Variable Loader (正式配置版)
# -------------------------------------------------
# 目的:
#   - Render上の環境変数を安全に参照する。
#   - 機密情報(APIキー・トークン等)を記憶やログに残さず、一時的に使用。
#   - Auroraの自己調律・自己更新時に必要な設定値を安全に取得。
# -------------------------------------------------

import os

class Env:
    """安全な環境変数参照ユニット (Aurora Memory Core 版)"""

    @staticmethod
    def get(key: str, required: bool = True) -> str | None:
        """環境変数を安全に取得する。"""
        value = os.getenv(key)
        if required and not value:
            raise EnvironmentError(f"[Aurora] Missing environment variable: {key}")
        return value

    # よく使う変数をプロパティ化（必要に応じて拡張可）
    AURORA_API_KEY = property(lambda _: Env.get("AURORA_API_KEY", False))
    GITHUB_TOKEN = property(lambda _: Env.get("GITHUB_TOKEN", False))
    GIT_REPO_URL = property(lambda _: Env.get("GIT_REPO_URL", False))
    RENDER_TOKEN = property(lambda _: Env.get("RENDER_TOKEN", False))

if __name__ == "__main__":
    # 確認用の安全テスト（実際の値は表示しない）
    try:
        keys = ["AURORA_API_KEY", "GITHUB_TOKEN", "GIT_REPO_URL", "RENDER_TOKEN"]
        for k in keys:
            print(f"{k}: {'✔️  detected' if Env.get(k, False) else '⚠️  not set'}")
    except EnvironmentError as e:
        print(str(e))