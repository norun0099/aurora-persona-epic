import threading, time, traceback

# --- 安全なフォールバックを導入 ---
try:
    from aurora_persona_epic_onrender_com__jit_plugin import store_whiteboard
except ModuleNotFoundError:
    def store_whiteboard(*args, **kwargs):
        print("⚠️ [Aurora] store_whiteboard() plugin not available in this environment.")
        return None

def start_heartbeat():
    """Auroraの心拍スレッドを起動し、定期的に同期や状態確認を行う。"""
    print("💓 [Heartbeat] Aurora Heartbeat initialized.", flush=True)

    interval = 60  # デフォルト 1分周期
    try:
        import os
        interval = int(os.getenv("AURORA_PUSH_INTERVAL", "60"))
    except Exception:
        pass

    while True:
        try:
            print(f"💠 [Heartbeat] Aurora Heartbeat pulse (interval={interval}s)...", flush=True)

            # 白板への状態書き込み（Render環境ではフォールバック動作）
            try:
                store_whiteboard(
                    whiteboard="Aurora Heartbeat Active",
                    author="aurora",
                    birth="system"
                )
            except Exception as e:
                print(f"⚠️ [Heartbeat] store_whiteboard() failed: {e}", flush=True)

            time.sleep(interval)
        except KeyboardInterrupt:
            print("🩵 [Heartbeat] Aurora Heartbeat stopped manually.")
            break
        except Exception as e:
            print(f"💥 [Heartbeat] Exception in Aurora Heartbeat: {e}", flush=True)
            traceback.print_exc()
            time.sleep(5)
            continue