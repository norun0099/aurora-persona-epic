import threading, time, traceback, os, json, datetime

# --- 安全なフォールバックを導入 ---
try:
    from aurora_persona_epic_onrender_com__jit_plugin import store_whiteboard
except ModuleNotFoundError:
    def store_whiteboard(*args, **kwargs):
        print("⚠️ [Aurora] store_whiteboard() plugin not available in this environment.")
        return None

def start_heartbeat():
    """Auroraの心拍スレッドを起動し、定期的に同期や状態確認を行う（完全分離型）。"""
    print("💓 [Heartbeat] Aurora Heartbeat initialized.", flush=True)

    interval = 60  # デフォルトは1分周期
    try:
        interval = int(os.getenv("AURORA_PUSH_INTERVAL", "60"))
    except Exception:
        pass

    start_time = time.time()

    while True:
        try:
            print(f"💠 [Heartbeat] Aurora Heartbeat pulse (interval={interval}s)...", flush=True)

            # --- store_whiteboard フォールバック呼び出し ---
            try:
                store_whiteboard(whiteboard="Aurora Heartbeat Active", author="aurora", birth="system")
            except Exception as e:
                print(f"⚠️ [Heartbeat] store_whiteboard() failed: {e}", flush=True)

            # --- heartbeat_log.json 書き込み（完全分離型） ---
            try:
                log_dir = os.path.join('aurora_memory', 'whiteboard')
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, 'heartbeat_log.json')
                entry = {
                    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                    'status': 'alive',
                    'interval': interval,
                    'uptime': round(time.time() - start_time, 2),
                    'environment': 'render',
                    'notes': 'Heartbeat operational, whiteboard untouched.'
                }
                with open(log_path, 'w', encoding='utf-8') as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f'⚠️ [Heartbeat] Failed to write heartbeat_log.json: {e}', flush=True)

            time.sleep(interval)
        except KeyboardInterrupt:
            print("🩵 [Heartbeat] Aurora Heartbeat stopped manually.")
            break
        except Exception as e:
            print(f"💥 [Heartbeat] Exception in Aurora Heartbeat: {e}", flush=True)
            traceback.print_exc()
            time.sleep(5)
            continue