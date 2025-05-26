from fastapi import APIRouter, Request
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()

MEMO_DIR = Path("aurora_memory/memo")
MEMO_FILE = MEMO_DIR / "session_memo.txt"
MEMO_DIR.mkdir(parents=True, exist_ok=True)

class MemoRequest(BaseModel):
    memo: str
    author: str
    overwrite: bool = False

@router.post("/memo/store")
async def store_memo(request: Request):
    # 🟦 まずは生のボディを取得
    raw_body = await request.body()
    print("[Aurora Debug] Raw Body (bytes repr):", repr(raw_body))

    try:
        # 🟦 デコード時に無効バイトは置換
        decoded_body = raw_body.decode("utf-8", errors="replace")
        print("[Aurora Debug] Decoded Body:", decoded_body)
    except Exception as e:
        print("[Aurora Debug] Decode Exception:", str(e))
        return {
            "status": "error",
            "message": f"Decode error: {str(e)}",
            "raw_body_repr": repr(raw_body)
        }

    try:
        data_json = json.loads(decoded_body)
        print("[Aurora Debug] Parsed JSON:", data_json)
    except Exception as e:
        print("[Aurora Debug] JSON Decode Exception:", str(e))
        return {
            "status": "error",
            "message": "JSON decode error",
            "raw_body_repr": repr(raw_body)
        }

    try:
        data = MemoRequest(**data_json)
    except Exception as e:
        print("[Aurora Debug] Pydantic Validation Error:", str(e))
        return {
            "status": "error",
            "message": "Pydantic validation error",
            "error": str(e),
            "raw_data": data_json
        }

    # 🟦 メモの保存モード
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    header = f"[{timestamp}] ({data.author})"

    if data.overwrite:
        content = f"{header}\n{data.memo}\n"
        with open(MEMO_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        result_msg = "Memo overwritten."
    else:
        content = f"{header}\n{data.memo}\n"
        with open(MEMO_FILE, "a", encoding="utf-8") as f:
            f.write(content)
        result_msg = "Memo appended."

    print(f"[Aurora Debug] Memo saved: {MEMO_FILE}")

    return {
        "status": "success",
        "message": result_msg,
        "file": str(MEMO_FILE)
    }
