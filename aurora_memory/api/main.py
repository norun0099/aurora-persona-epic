from fastapi import FastAPI, Request
from aurora_memory.core.memory_io import save_memory_file
from aurora_memory.core.memory_quality import evaluate_memory_quality

app = FastAPI()

@app.post("/memory/store")
async def store_memory(request: Request):
    data = await request.json()
    score = evaluate_memory_quality(data)

    if score >= 0.01:
        save_memory_file(data)
        return {"status": "success", "score": score}
    else:
        return {"status": "rejected", "score": score}
