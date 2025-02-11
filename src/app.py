from fastapi import (
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import model_router
from tools.connect import get_port

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(model_router.router)
# app.include_router(ws_router.router)


@app.get("/", tags=["Test model handler alive"])
async def check_alive():
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "message": "Model handler is alive."},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=get_port())
