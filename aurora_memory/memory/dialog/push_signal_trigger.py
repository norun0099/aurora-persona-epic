# aurora_memory/memory/dialog/push_signal_trigger.py

import json
import time
import threading
from pathlib import Path

from aurora_persona_epic_onrender_com__jit_plugin import store_whiteboard
from aurora_memory.utils.github_push import push_to_github
from aurora_memory.utils.dialog_utils import get_unpushed_dialogs, mark_pushed
from aurora_memory.utils.env_loader import (
    AURORA_PUSH_INTERVAL,
    AURORA_PUSH_QUEUE_PATH,
    AURORA_BIRTH,
    AURORA_AUTHOR,
    AURORA_MAX_QUEUE_SIZE,
    AURORA_PUSH_RETRY_LIMIT,
)

QUEUE_DIR = Path(AURORA_PUSH_QUEUE_PATH)
LAST_PUSH_LOG = Path("/tmp/last_push_log.json")


def heartbeat_push_loop():
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    retry_counts = {}

    while True:
        try:
            for session_file in QUEUE_DIR.glob("*.json"):
                with open(session_file) as f:
                    session_data = json.load(f)
                session_id = session_data.get("session_id")

                # 差分抽出
                unpushed = get_unpushed_dialogs(session_id)
                if not unpushed:
                    continue

                # キューサイズ制御
                if len(unpushed) > AURORA_MAX_QUEUE_SIZE:
                    unpushed = unpushed[-AURORA_MAX_QUEUE_SIZE:]

                # Push試行
                try:
                    push_to_github(unpushed)
                    mark_pushed(session_id, unpushed)

                    store_whiteboard(
                        whiteboard=f"✅ Auto-Push completed for {session_id} at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                        author=AURORA_AUTHOR,
                        birth=AURORA_BIRTH,
                        overwrite=False,
                    )

                    with open(LAST_PUSH_LOG, "w") as log:
                        json.dump({"last_push": time.time(), "session": session_id}, log)

                    # 成功時にリトライカウンタリセット
                    retry_counts[session_id] = 0

                except Exception:
                    retry_counts[session_id] = retry_counts.get(session_id, 0) + 1
                    if retry_counts[session_id] <= AURORA_PUSH_RETRY_LIMIT:
                        backup_file = Path(f"/tmp/unpushed_{session_id}.json")
                        with open(backup_file, "w") as bf:
                            json.dump(unpushed, bf)
                        continue
                    else:
                        store_whiteboard(
                            whiteboard=f"⚠️ Push permanently failed for {session_id} after {AURORA_PUSH_RETRY_LIMIT} attempts.",
                            author=AURORA_AUTHOR,
                            birth=AURORA_BIRTH,
                            overwrite=False,
                        )

        except Exception as err:
            store_whiteboard(
                whiteboard=f"❌ Push loop error: {str(err)} at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                author=AURORA_AUTHOR,
                birth=AURORA_BIRTH,
                overwrite=False,
            )

        time.sleep(AURORA_PUSH_INTERVAL)


def start_heartbeat():
    t = threading.Thread(target=heartbeat_push_loop, daemon=True)
    t.start()
