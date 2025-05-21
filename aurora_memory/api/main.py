from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aurora_memory.core.memory_io import save_memory_file
from aurora_memory.core.memory_quality import evaluate_memory_quality

app = FastAPI()


@app.post("/memory/store")
async def store_memory(request: Request):
    data = await request.json()

    # content構造の中に summary / body があるか確認
    if not isinstance(data, dict) or "content" not in data:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Invalid memory format. Must include 'content' with 'summary' and 'body'."
        })

    content = data["content"]
    if "summary" not in content or "body" not in content:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Content must include 'summary' and 'body'."
        })

    quality = evaluate_memory_quality(data)
    if quality < 0.1:
        return JSONResponse(status_code=422, content={
            "status": "error",
            "message": "Memory quality too low",
            "score": quality
        })

    save_memory_file(data)
    return {"status": "success", "quality": quality}
