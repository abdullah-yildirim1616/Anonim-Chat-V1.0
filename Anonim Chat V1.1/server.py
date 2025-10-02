from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List

app = FastAPI()

# Oda bazlı bağlantıları yöneten sınıf
class ConnectionManager:
    def __init__(self):
        # her oda için ayrı bağlantı listesi
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.rooms[room_id].remove(websocket)
        if not self.rooms[room_id]:  # oda boşsa sil
            del self.rooms[room_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_room(self, room_id: str, message: str):
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_room(room_id, f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
