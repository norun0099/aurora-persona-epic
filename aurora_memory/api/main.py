from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

from aurora_memory.core.memory_io import save_memory_file
from aurora_memory.core.memory_quality import evaluate_memory_quality

app = FastAPI()

@app.post("/memory/store")
async def store_memory(request: Request):
    data = await request.json()
    score = evaluate_memory_quality(data)

    if score >= 0.01:
        save_memory_file(data)
        return {"status": "success", "score": round(score, 4)}
    else:
        return {"status": "rejected", "score": round(score, 4)}

# ValueError を 400 に変換
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )

# バリデーションエラーの処理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return await request_validation_exception_handler(request, exc)
