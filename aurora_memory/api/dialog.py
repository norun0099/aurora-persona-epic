from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import os
import json
import uuid

router = APIRouter()

# ダイアログ保存ディレクトリ（GitHub永続化対象）
DIALOG_DIR = Path("aurora_memory/memory/dialog")
DIALOG_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# Data Models
# -------------------------
class DialogTurn(BaseModel):
    turn: int
    speaker: str   # "user" or "aurora"
    content: str   # 元の発言
    summary: str | None = None  # Auroraが生成する要約（任意）
    timestamp: str
    layer: str | None = None  # strategy | organize | implement | None

class DialogRequest(BaseModel):
    session_id: str | None = None
    turn: DialogTurn

class DialogSession(BaseModel):
    session_id: str
    created: str
    updated: str
    dialog: list[DialogTurn] = []

# -------------------------
# Helpers
# -------------------------
def get_dialog_path(session_id: str) -> Path:
    return DIALOG_DIR / f"{session_id}.json"

def generate_session_id() -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    short_uuid = str(uuid.uuid4())[:6]
    return f"{now}-{short_uuid}"

# -------------------------
# API Routes
# -------------------------
@router.post("/dialog/store")
def store_dialog(req: DialogRequest):
    """1ターン分の発言をダイアログに追記し、GitHubへpushする"""
    session_id = req.session_id or generate_session_id()
    turn = req.turn

    path = get_dialog_path(session_id)
    now = datetime.now().isoformat()

    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            session = json.load(f)
    else:
        session = {
            "session_id": session_id,
            "created": now,
            "updated": now,
            "dialog": []
        }

    turn_dict = turn.dict()
    # Auroraがsummaryを渡さなかった場合は暫定的にcontentを切り詰めて補う
    if not turn_dict.get("summary"):
        turn_dict["summary"] = turn_dict["content"][:40] + ("…" if len(turn_dict["content"]) > 40 else "")

    session["dialog"].append(turn_dict)
    session["updated"] = now

    with path.open("w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    # 🔹 GitHubへpush
    from aurora_memory.utils.git_helper import push_memory_to_github
    push_result = push_memory_to_github(path, f"Add new dialog turn for {session_id}")

    return {
        "status": "success",
        "session_id": session_id,
        "turns": len(session["dialog"]),
        "push_result": push_result
    }

@router.get("/dialog/latest")
def get_latest_dialog(session_id: str):
    """指定されたセッションの最新ダイアログを返す"""
    path = get_dialog_path(session_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dialog not found")
    with path.open("r", encoding="utf-8") as f:
        session = json.load(f)
    return session

@router.get("/dialog/history")
def get_dialog_history():
    """保存されている全セッションの一覧を返す"""
    files = [f for f in os.listdir(DIALOG_DIR) if f.endswith(".json")]
    sessions = []
    for file in files:
        with open(DIALOG_DIR / file, "r", encoding="utf-8") as f:
            data = json.load(f)
            sessions.append({
                "session_id": data["session_id"],
                "created": data["created"],
                "updated": data["updated"],
                "turns": len(data["dialog"])
            })
    return sessions
