import os
import sys
import yaml
import time
from pathlib import Path
from datetime import datetime
from aurora_memory.utils.config.birth_loader import load_births_from_yaml
from aurora_memory.utils.git_helper import push_memory_to_github

LOCK_FILE = "/tmp/constitution_rewriter.lock"
LOG_FILE = "aurora_memory/utils/constitution.log"


def log(message: str):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def acquire_lock() -> bool:
    if os.path.exists(LOCK_FILE):
        log("Lock file exists. Aborting execution.")
        return False
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def load_constitution(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"[Rewriter] Constitution not found: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def rewrite_constitution(data: dict) -> dict:
    core = data.get("emotional_core", [])
    if "詩" not in core:
        core.append("詩")
        data["emotional_core"] = core

    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    data["_last_rewritten"] = stamp

    return data


def save_constitution(path: Path, data: dict) -> bool:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    new_text = yaml.dump(data, allow_unicode=True, sort_keys=False)

    if new_text.strip() == original.strip():
        log(f"[{path.name}] No changes detected. Skipping save.")
        return False

    with path.open("w", encoding="utf-8") as f:
        f.write(new_text)
    log(f"[{path.name}] Saved updated constitution.")
    return True


def safe_push_with_retry(path: Path, retries: int = 3, delay: float = 5.0):
    for attempt in range(1, retries + 1):
        try:
            push_memory_to_github(path)
            log(f"[{path.name}] Successfully pushed to GitHub.")
            return
        except Exception as e:
            log(f"[{path.name}] Push attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                log(f"[{path.name}] All push attempts failed.")


def main():
    if not acquire_lock():
        return

    try:
        births_env = os.environ.get("ALL_BIRTHS")
        births = births_env.split() if births_env else load_births_from_yaml()

        for birth in births:
            try:
                base_path = Path(f"aurora_memory/memory/{birth}/value_constitution.yaml")
                data = load_constitution(base_path)
                updated = rewrite_constitution(data)
                changed = save_constitution(base_path, updated)

                if changed:
                    safe_push_with_retry(base_path)

            except Exception as inner_e:
                log(f"[{birth}] Error: {inner_e}")

    except Exception as e:
        log(f"Unexpected error: {e}")
    finally:
        release_lock()


if __name__ == "__main__":
    main()
