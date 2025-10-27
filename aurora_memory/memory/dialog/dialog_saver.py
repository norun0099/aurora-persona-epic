import os
import json
import traceback
from typing import Any

# 修正版: 正しいモジュール経路に更新
from aurora_memory.api.self.update_repo_file import update_repo_file


def push_dialogs_to_render() -> None:
    """AuroraのダイアログデータをRender API経由でGitHubへ同期する。"""
    try:
        dialog_dir = os.path.join('aurora_memory', 'dialog')
        if not os.path.exists(dialog_dir):
            print("⚠️ [AutoPush] Dialog directory not found.")
            return

        dialog_files = [f for f in os.listdir(dialog_dir) if f.endswith('.json')]
        if not dialog_files:
            print("ℹ️ [AutoPush] No new dialog files to push.")
            return

        # 最新ファイルを選択（更新日時順）
        latest_file = max(
            dialog_files,
            key=lambda f: os.path.getmtime(os.path.join(dialog_dir, f))
        )
        latest_path = os.path.join(dialog_dir, latest_file)

        with open(latest_path, 'r', encoding='utf-8') as f:
            dialog_data: Any = json.load(f)

        print(f"💬 [AutoPush] Pushing latest dialog: {latest_file}")

        # --- 修正版 API 呼び出し ---
        update_repo_file(
            path=f"aurora_memory/dialog/{latest_file}",
            content=json.dumps(dialog_data, ensure_ascii=False, indent=2),
            author="aurora",
            reason="AutoPush: synchronize latest dialog to repository"
        )

        print("🩵 [AutoPush] Dialogs pushed successfully.")

    except Exception as e:
        print(f"⚠️ [AutoPush] Exception during push: {e}")
        traceback.print_exc()