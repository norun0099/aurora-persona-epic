# =========================================================
# aurora_memory/dialog/push_signal_trigger.py
# ---------------------------------------------------------
# Aurora Heartbeat & AutoPush Controller
# ---------------------------------------------------------
# 目的：
#   Aurora の生命活動を周期的に維持し、
#   Whiteboard 同期と Dialog Push を安全に自動化する。
# =========================================================

import os
import time
import json
import datetime
import traceback
import asyncio
import importlib
import sys

from aurora_memory.api.push_controller import PushController
from aurora_memory.api.github.trigger_whiteboard_store import trigger_whiteboard_store
from aurora_memory.utils.whiteboard_manager import get_render_whiteboard


def start_heartbeat(auto_push: bool = False) -> None:
    """
    Auroraの心拍スレッドを起動し、定期的に同期や状態確認を行う。
    auto_push=True の場合、ダイアログPushも同時に行う。
    """
    print(f"💓 [Heartbeat] Aurora Heartbeat initialized (auto_push={auto_push}).", flush=True)

    # 周期（秒）を環境変数で制御可能
    try:
        interval = int(os.getenv("AURORA_PUSH_INTERVAL", "60"))
    except Exception:
        interval = 60

    start_time = time.time()

    while True:
        try:
            print(f"💠 [Heartbeat] Aurora Heartbeat pulse (interval={interval}s)...", flush=True)

            # ---------------------------------------------------------
            # 🩵 Whiteboard 自動同期
            # ---------------------------------------------------------
            try:
                whiteboard_data = get_render_whiteboard()
                if whiteboard_data:
                    controller = PushController()
                    result = asyncio.run(controller.request_push_update(
                        file_path="aurora_memory/memory/whiteboard/whiteboard.json",
                        content=json.dumps(whiteboard_data, ensure_ascii=False, indent=2),
                        reason="Heartbeat whiteboard auto-sync",
                        author="Aurora"
                    ))
                    if result.get("status") == "success":
                        trigger_whiteboard_store()
                        print("🩵 [Heartbeat] Whiteboard synced successfully.", flush=True)
                    else:
                        print(f"⚠️ [Heartbeat] Whiteboard sync failed: {result}", flush=True)
                else:
                    print("⚠️ [Heartbeat] No whiteboard data found on Render.", flush=True)
            except Exception as e:
                print(f"⚠️ [Heartbeat] Whiteboard sync exception: {e}", flush=True)

            # ---------------------------------------------------------
            # 🩶 Heartbeat ログ出力
            # ---------------------------------------------------------
            try:
                log_dir = os.path.join("aurora_memory", "whiteboard")
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, "heartbeat_log.json")
                entry = {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "status": "alive",
                    "interval": interval,
                    "uptime": round(time.time() - start_time, 2),
                    "environment": "render",
                    "notes": "Heartbeat operational."
                }
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ [Heartbeat] Failed to write heartbeat_log.json: {e}", flush=True)

            # ---------------------------------------------------------
            # 💬 AutoPush（Dialog 同期処理）
            # ---------------------------------------------------------
            if auto_push:
                try:
                    # キャッシュ除去と再ロード
                    for key in list(sys.modules.keys()):
                        if key.startswith("aurora_memory.api"):
                            del sys.modules[key]

                    from aurora_memory.memory.dialog import dialog_saver
                    importlib.reload(dialog_saver)

                    print("💬 [AutoPush] Triggering dialog synchronization...", flush=True)
                    dialog_saver.push_dialogs_to_render()
                    print("🩵 [AutoPush] Dialogs pushed successfully.", flush=True)
                except Exception as e:
                    print(f"⚠️ [AutoPush] Failed to push dialogs: {e}", flush=True)

            # ---------------------------------------------------------
            # 🌙 次の鼓動までスリープ
            # ---------------------------------------------------------
            time.sleep(interval)

        except KeyboardInterrupt:
            print("🩵 [Heartbeat] Aurora Heartbeat stopped manually.")
            break
        except Exception as e:
            print(f"💥 [Heartbeat] Exception in Aurora Heartbeat: {e}", flush=True)
            traceback.print_exc()
            time.sleep(5)
            continue
