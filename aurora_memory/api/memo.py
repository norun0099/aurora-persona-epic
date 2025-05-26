# aurora_memory/api/memo.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import json

router = APIRouter()

# ディレクトリパス
MEMO_DIR = Path("aurora_memory/memory/memos")
MEMO_DIR.mkdir(parents=True, exist_ok=True)

# メモデータの受け取り構造
class MemoRequest(BaseModel):
    memo: str
    author: str
    overwrite: bool = False

@router.post("/memo/store")
async def store_memo(request: Request):
    # 🟦 受信した生のボディをデバッグ出力
    raw_body = await request.body()
    print("[Aurora Debug] Raw Body:", raw_body.decode("utf-8"))

    try:
        # 🟦 JSONとしてロードを試みる
        data_json = json.loads(raw_body)
        print("[Aurora Debug] Parsed JSON:", data_json)
    except json.JSONDecodeError as e:
        print("[Aurora Debug] JSON Decode Error:", str(e))
        return {
            "status": "error",
            "message": "JSON decode error",
            "raw_body": raw_body.decode("utf-8")
        }

    try:
        # 🟦 Pydanticのモデルに変換
        data = MemoRequest(**data_json)
    except Exception as e:
        print("[Aurora Debug] Pydantic Validation Error:", str(e))
        return {
            "status": "error",
            "message": "Pydantic validation error",
            "error": str(e),
            "raw_data": data_json
        }

    # 🟦 ファイル名を作成（例: author_年月日時分秒.json）
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{data.author}_{timestamp}.json"
    file_path = MEMO_DIR / file_name

    # 🟦 ファイル保存処理
    if data.overwrite:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
    else:
        counter = 1
        while file_path.exists():
            file_path = MEMO_DIR / f"{data.author}_{timestamp}_{counter}.json"
            counter += 1
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)

    return {
        "status": "success",
        "message": "メモが保存されました（デバッグログ含む）",
        "file_path": str(file_path),
        "memo": data.dict()
    }
