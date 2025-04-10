from fastapi import FastAPI, WebSocket, Request
from typing import List


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: dict, sender: WebSocket):
        for connection in self.connections:
            if connection != sender:
                await connection.send_json(data)