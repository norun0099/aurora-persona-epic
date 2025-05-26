# aurora_memory/api/memo.py

from fastapi import APIRouter
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
async def store_memo(data: MemoRequest):
    # 🟦 受け取ったデータをデバッグ出力
    print("[Aurora Debug] Memo Body:", data.dict())

    # 🟦 ファイル名を作成（例: author_年月日時分秒.json）
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{data.author}_{timestamp}.json"
    file_path = MEMO_DIR / file_name

    # 🟦 ファイル保存処理
    if data.overwrite:
        # overwrite=Trueの場合は同名ファイルに上書き（存在しなければ新規作成）
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
    else:
        # overwrite=Falseなら、既存ファイルがあれば別名で保存
        counter = 1
        original_file_path = file_path
        while file_path.exists():
            file_path = MEMO_DIR / f"{data.author}_{timestamp}_{counter}.json"
            counter += 1
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)

    return {
        "status": "success",
        "message": "メモが保存されました",
        "file_path": str(file_path),
        "memo": data.dict()
    }
