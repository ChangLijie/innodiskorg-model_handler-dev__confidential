from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from utils import manager

router = APIRouter()


@router.websocket("/ws/{uuid}")
async def websocket_endpoint(websocket: WebSocket, uuid: str):
    try:
        status = await manager.connect(uuid, websocket)
        while status:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(uuid, websocket)
