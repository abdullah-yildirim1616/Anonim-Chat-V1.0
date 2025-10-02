from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
import uuid

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}
        self.waiting: List[WebSocket] = []  # bekleyen kullanıcılar

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # Eğer bekleyen biri varsa, ikisini eşleştir
        if self.waiting:
            partner = self.waiting.pop(0)
            room_id = str(uuid.uuid4())  # benzersiz oda ID
            self.rooms[room_id] = [partner, websocket]

            # Herkese "eşleştin" mesajı gönder
            await partner.send_text("Eşleştin! Sohbete başlayabilirsin.")
            await websocket.send_text("Eşleştin! Sohbete başlayabilirsin.")
        else:
            # Kimse yoksa beklemeye ekle
            self.waiting.append(websocket)
            await websocket.send_text("Beklemeye alındın, biri bağlanınca eşleşeceksin.")

    def disconnect(self, websocket: WebSocket):
        # Bekleyen listeden çıkar
        if websocket in self.waiting:
            self.waiting.remove(websocket)

        # Oda içinde ise çıkar
        for room_id, connections in list(self.rooms.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:  # oda boş kaldıysa sil
                    del self.rooms[room_id]

    async def send_to_partner(self, websocket: WebSocket, message: str):
        # Oda bul
        for room_id, connections in self.rooms.items():
            if websocket in connections:
                for conn in connections:
                    if conn != websocket:  # sadece karşı tarafa gönder
                        await conn.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_partner(websocket, f"Mesaj: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
