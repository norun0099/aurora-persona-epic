from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from aurora_memory.core.memory_io import load_memory_files, save_memory_file
from aurora_memory.core.memory_quality import evaluate_memory_quality

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Aurora Memory API is running."}

@app.post("/load")
async def load_memory(request: Request):
    try:
        data = await request.json()
        result = load_memory_files(data)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/save")
async def save_memory(request: Request):
    try:
        data = await request.json()
        save_memory_file(data)
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/memory/store")
async def store_memory(request: Request):
    try:
        data = await request.json()

        if not isinstance(data, dict) or "summary" not in data or "body" not in data:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": "Invalid memory format. Must include 'summary' and 'body'."
            })

        if not evaluate_memory_quality(data):
            return JSONResponse(status_code=403, content={
                "status": "rejected",
                "message": "Memory quality too low to store."
            })

        # 既存ファイル読み込み
        memory = load_memory_files({})
        memory.setdefault("memories", []).append(data)

        # 保存
        save_memory_file(memory)

        return JSONResponse(content={"status": "stored", "message": "Memory stored successfully."})

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })
