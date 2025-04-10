import json

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette import status
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.routers import category, products, auth, permission, users, review, celery
from app.routers.websocket import ConnectionManager

load_dotenv()

app = FastAPI(swagger_ui_parameters={"persistAuthorization": True})
templates = Jinja2Templates(directory="app/templates")
manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            formatted_message = message_data.get('message', '')
            await manager.broadcast(
                {"senderId": str(client_id), "message": formatted_message}, websocket
            )
    except WebSocketDisconnect as e:
        manager.connections.remove(websocket)
        print(f'Connection closed {e.code}')

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "https://example.com",
    "null"
]
allowed_hosts = ["example.com", "*.example.com", "127.0.0.1"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.get("/health_check", status_code=status.HTTP_200_OK)
async def welcome() -> dict:
    return {"message": "My e-commerce app"}


app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(users.router)
app.include_router(review.router)
app.include_router(celery.router)
# app.include_router(websocket.router)
 