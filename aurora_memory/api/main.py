from fastapi import FastAPI, Request
from aurora_memory.core.memory_io import save_memory_file, load_memory_files

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "alive", "message": "Aurora Memory API is online."}

@app.post("/memory/store")
async def store_memory(request: Request):
    data = await request.json()
    result = save_memory_file(data)
    return result

@app.get("/memory/load")
async def load_memory(request: Request):
    return load_memory_files({})
