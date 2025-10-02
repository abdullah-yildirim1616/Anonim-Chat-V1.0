from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, Depends
from fastapi.responses import HTMLResponse
from typing import Dict, List
import uuid

app = FastAPI()

# Kullanıcı kayıtlarını tutacağımız hafızadaki "veritabanı"
users: Dict[str, dict] = {}       # user_id -> user_info
waiting: List[str] = []           # bekleyen user_id listesi
rooms: Dict[str, List[str]] = {}  # room_id -> [user1, user2]
connections: Dict[str, WebSocket] = {}  # user_id -> WebSocket

# Basit admin kontrolü (gerçek projede JWT veya OAuth kullanılmalı)
ADMIN_PASSWORD = "1234"

# Kayıt endpoint
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    user_id = str(uuid.uuid4())[:6]  # kısa bir benzersiz ID
    users[user_id] = {"username": username, "password": password}
    return {"message": "Kayıt başarılı", "user_id": user_id}

# Admin panel (HTML sayfa döner)
@app.get("/admin")
async def admin_panel(password: str):
    if password != ADMIN_PASSWORD:
        return HTMLResponse("<h1>403 Forbidden</h1>", status_code=403)

    # basit butonlu admin sayfası
    return HTMLResponse("""
    <html>
      <body>
        <h1>Admin Panel</h1>
        <form action="/match" method="post">
            <button type="submit">Eşleştir</button>
        </form>
      </body>
    </html>
    """)

# Admin eşleştirme işlemi
@app.post("/match")
async def match(password: str = Form(...)):
    if password != ADMIN_PASSWORD:
        return {"error": "Yetkisiz"}

    # bekleyen kullanıcıları ikili eşleştir
    matched = []
    while len(waiting) >= 2:
        user1 = waiting.pop(0)
        user2 = waiting.pop(0)
        room_id = str(uuid.uuid4())
        rooms[room_id] = [user1, user2]
        matched.append((user1, user2))

        # Eşleşme mesajı gönder
        if user1 in connections:
            await connections[user1].send_text(f"{user2} ile eşleştin.")
        if user2 in connections:
            await connections[user2].send_text(f"{user1} ile eşleştin.")

    return {"matched": matched}

# WebSocket endpoint
@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    connections[user_id] = websocket

    # kullanıcıyı bekleyen listesine ekle
    if user_id not in waiting:
        waiting.append(user_id)
        await websocket.send_text("Beklemeye alındın. Admin eşleştirecek.")

    try:
        while True:
            data = await websocket.receive_text()
            # Kullanıcının odasını bul
            for room_id, users_in_room in rooms.items():
                if user_id in users_in_room:
                    # Partneri bul
                    partner = users_in_room[0] if users_in_room[1] == user_id else users_in_room[1]
                    if partner in connections:
                        await connections[partner].send_text(f"{user_id}: {data}")
    except WebSocketDisconnect:
        if user_id in waiting:
            waiting.remove(user_id)
        del connections[user_id]
