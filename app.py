from fastapi import (
    FastAPI,
)
from fastapi.responses import JSONResponse
from routers import model_router, ws_router

app = FastAPI()
app.include_router(model_router.router)
app.include_router(ws_router.router)


@app.get("/", tags=["Test model handler alive"])
async def check_alive():
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "message": "Model handler is alive."},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
