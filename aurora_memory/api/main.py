from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from aurora_memory.core.memory_io import load_memory_files, save_memory_file

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
