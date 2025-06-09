from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import yaml
import json
import os
import subprocess
import shutil
import httpx
from typing import Optional

from aurora_memory.utils.gpt_sender import send_memo_to_gpt  # 同期版は残す（暫定）

router = APIRouter()

# 設定ファイルのパス
CONDITION_FILE = Path("aurora_memory/config/memo_conditions.yaml")

# メモデータの受け取り構造
class MemoRequest(BaseModel):
    birth: str
    memo: str
    author: str
    overwrite: bool = False

# 条件を読み込む
def load_conditions():
    with open(CONDITION_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 条件をチェックする関数
def check_conditions(memo_text: str, conditions: dict) -> bool:
    for keyword in conditions.get("keywords", []):
        if keyword in memo_text:
            return True
    if len(memo_text) >= conditions.get("min_length", 0):
        return True
    return False

# GitHubへpushする関数（無効化中）
def push_memory_to_github(file_path: Path):
    return {"status": "skipped", "message": "Push disabled for stability"}

# GPT送信を非同期で実行
def get_endpoint(birth: str) -> str:
    return f"https://aurora-gpt-endpoints.com/{birth}"

async def send_memo_to_gpt_async(birth: str, memo_text: str) -> dict:
    endpoint = get_endpoint(birth)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(endpoint, json={"birth": birth, "memo": memo_text})
            return {"status": "success", "response": resp.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/memo/store")
async def store_memo(data: MemoRequest):
    print("[Aurora Debug] Memo Body:", data.dict())

    memo_dir = Path("aurora_memory/memory") / data.birth / "memo"
    memo_dir.mkdir(parents=True, exist_ok=True)

    conditions = load_conditions()
    if not check_conditions(data.memo, conditions):
        return {
            "status": "skipped",
            "message": "メモ保存条件を満たしていません",
            "memo": data.memo
        }

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"{data.author}_{timestamp}.json"
    file_path = memo_dir / file_name

    try:
        if data.overwrite:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data.dict(), f, ensure_ascii=False, indent=2)
        else:
            counter = 1
            while file_path.exists():
                file_path = memo_dir / f"{data.author}_{timestamp}_{counter}.json"
                counter += 1
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data.dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {
            "status": "error",
            "message": f"メモ保存中にエラーが発生しました: {str(e)}"
        }

    push_result = push_memory_to_github(file_path)
    gpt_result = await send_memo_to_gpt_async(data.birth, data.memo)

    return {
        "status": "success",
        "message": "メモが保存されました",
        "file_path": str(file_path),
        "memo": data.dict(),
        "push_result": push_result,
        "gpt_result": gpt_result,
    }

@router.get("/memo/latest")
async def get_latest_memo(birth: str):
    source_dir = Path("aurora_memory/memory") / birth / "memo"
    temp_dir = Path("aurora_memory/memory/memos")
    temp_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        raise HTTPException(status_code=404, detail=f"birth '{birth}' のメモディレクトリが存在しません")

    json_files = list(source_dir.glob("*.json"))
    if not json_files:
        raise HTTPException(status_code=404, detail=f"birth '{birth}' にメモファイルが存在しません")

    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    temp_path = temp_dir / latest_file.name

    shutil.copy(latest_file, temp_path)

    with open(temp_path, "r", encoding="utf-8") as f:
        memo_data = json.load(f)

    return {
        "status": "success",
        "birth": birth,
        "copied_to": str(temp_path),
        "memo": memo_data
    }

@router.post("/function/store_memo")
async def store_memo_via_function(data: MemoRequest):
    return await store_memo(data)
