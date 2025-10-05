from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

router = APIRouter()

JST = timezone(timedelta(hours=9), name="JST")


@router.get("/time/now", summary="現在のJST時刻を返す", tags=["Time"])  # type: ignore[misc]
def get_current_time() -> Dict[str, Any]:
    """
    現在の日本標準時（JST）を返します。
    """
    now_jst = datetime.now(JST)
    return {
        "datetime_jst": now_jst.isoformat(),
        "hour": now_jst.hour,
        "minute": now_jst.minute,
        "second": now_jst.second,
    }
