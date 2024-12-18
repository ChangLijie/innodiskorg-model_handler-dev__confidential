import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Dict, List

from fastapi import WebSocket

from utils import config_logger

WS_CONFIG = config_logger("ws.log", "w", "info")


class WSManager:
    def __init__(self, max_workers: int = 10, close_time: int = 10):
        self.rooms: Dict[str, List[WebSocket]] = defaultdict(list)
        self.message_cache: Dict[str, Queue] = defaultdict(Queue)
        self.broadcast_in_progress: Dict[str, bool] = defaultdict(bool)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.close_time = close_time
        WS_CONFIG.info("Start WS server.")

    def create_room(self, uuid: str):
        try:
            if uuid not in self.rooms:
                self.rooms[uuid] = []
                self.message_cache[uuid] = Queue()
                self.broadcast_in_progress[uuid] = False
                WS_CONFIG.info(f"Room created with task: {uuid}")
            else:
                WS_CONFIG.debug(f"Room was created: {uuid}")
        except Exception as e:
            WS_CONFIG.error(f"Failed to created room: {uuid}.detail :{e}")

    def room_exists(self, uuid: str) -> bool:
        return uuid in self.rooms

    async def connect(self, uuid: str, websocket: WebSocket):
        try:
            if not self.room_exists(uuid):
                await websocket.close(code=1000)
                WS_CONFIG.warning(f"Room {uuid} does not exist. Connection refused.")
                return False

            await websocket.accept()
            self.rooms[uuid].append(websocket)
            WS_CONFIG.info(f"Client connected to room: {uuid}")

            if not self.broadcast_in_progress[uuid]:
                self.broadcast_in_progress[uuid] = True
                asyncio.create_task(self._broadcast_cached_messages(uuid))
            return True
        except Exception as e:
            WS_CONFIG.error(f"Failed to connect room: {uuid}.detail :{e}")

    async def _broadcast_cached_messages(self, uuid: str):
        try:
            WS_CONFIG.info(f"Started broadcasting loop for room: {uuid}")

            while True:
                if uuid not in self.rooms or not self.rooms[uuid]:
                    WS_CONFIG.warning(f"Room {uuid} has no users. Stopping broadcast.")
                    break

                while not self.message_cache[uuid].empty():
                    message = self.message_cache[uuid].get()
                    for websocket in self.rooms[uuid]:
                        try:
                            await websocket.send_json(message)
                            WS_CONFIG.info(
                                f"Broadcasted cached message to room {uuid}: {message}"
                            )

                        except Exception as e:
                            WS_CONFIG.error(
                                f"Error broadcasting message to room {uuid}: {e}"
                            )

                    if message == {"end": True}:
                        WS_CONFIG.debug(
                            f"Received 'end' message for room {uuid}. Closing in 10 seconds..."
                        )

                        await asyncio.sleep(self.close_time)
                        await self._close_room(uuid)
                        return

                await asyncio.sleep(1)
        except Ellipsis as e:
            WS_CONFIG.error(f"Failed to connect room: {uuid}.detail :{e}")
        finally:
            self.broadcast_in_progress[uuid] = False
            WS_CONFIG.info(f"Finished broadcasting messages for room: {uuid}")

    def disconnect(self, uuid: str, websocket: WebSocket):
        try:
            if uuid in self.rooms and websocket in self.rooms[uuid]:
                self.rooms[uuid].remove(websocket)
                WS_CONFIG.debug(f"Client disconnected from room: {uuid}")

                if not self.rooms[uuid]:
                    del self.rooms[uuid]
                    WS_CONFIG.warning(f"Room {uuid} is now empty and removed.")
        except Ellipsis as e:
            WS_CONFIG.error(f"Failed to connect room: {uuid}.detail :{e}")

    async def send(self, uuid: str, message: dict):
        try:
            if uuid in self.message_cache:
                self.message_cache[uuid].put(message)
                WS_CONFIG.info(f"Message added to queue for room {uuid}: {message}")

            else:
                WS_CONFIG.warning(
                    f"Error: Room {uuid} does not exist, message not cached."
                )

        except Ellipsis as e:
            WS_CONFIG.error(f"Failed to connect room: {uuid}.detail :{e}")

    async def _close_room(self, uuid: str):
        if uuid in self.rooms:
            WS_CONFIG.warning(f"Closing room {uuid} and all its connections...")

            tasks = []
            for websocket in self.rooms[uuid]:
                try:
                    tasks.append(self._safe_close(websocket))  # 將關閉操作加入任務列表
                except Exception as e:
                    WS_CONFIG.error(
                        f"Error scheduling close for websocket in room {uuid}: {e}"
                    )

            if tasks:
                await asyncio.gather(*tasks)

            self.rooms.pop(uuid, None)
            self.message_cache.pop(uuid, None)
            self.broadcast_in_progress.pop(uuid, None)
            WS_CONFIG.warning(
                f"Room {uuid} and its resources have been successfully removed."
            )

    async def _safe_close(self, websocket: WebSocket):
        try:
            await websocket.close()
            WS_CONFIG.debug("WebSocket closed successfully.")

        except Exception as e:
            WS_CONFIG.error(f"Error closing WebSocket: {e}")


manager = WSManager()
