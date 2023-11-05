
from fastapi import FastAPI, HTTPException
import uvicorn
import os
from server import open_router
app = FastAPI(title="DemoServer", version="0.1.0")
app.include_router(open_router)

if __name__ == "__main__":
    uvicorn.run(
        f"{os.path.splitext(os.path.basename(__file__))[0]}:app",
        host="0.0.0.0",
        port=8000,
        workers=2,
    )