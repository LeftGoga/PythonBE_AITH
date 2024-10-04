from dataclasses import dataclass, field
import random
import string
from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

chat_router =  APIRouter(prefix = "/chat")

@dataclass(slots=True)
class Broadcaster:
    subscribers: List[WebSocket] = field(init=False, default_factory=list)

    async def subscribe(self, ws: WebSocket) -> None:
        await ws.accept()
        self.subscribers.append(ws)

    async def unsubscribe(self, ws: WebSocket) -> None:
        self.subscribers.remove(ws)

    async def publish(self, message: str) -> None:
        for ws in self.subscribers:
            await ws.send_text(message)


chat_broadcasters: Dict[str, Broadcaster] = {}


def generate_random_username():
    return ''.join(random.choices(string.ascii_letters, k=8))

@chat_router.websocket("/{chat_name}")
async def ws_chat(ws: WebSocket, chat_name: str):
    client_id = uuid4()
    username = uuid4()


    if chat_name not in chat_broadcasters:
        chat_broadcasters[chat_name] = Broadcaster()
    broadcaster = chat_broadcasters[chat_name]

    await broadcaster.subscribe(ws)
    await broadcaster.publish(f"client {client_id} ({username}) subscribed to {chat_name}")

    try:
        while True:
            text = await ws.receive_text()
            formatted_message = f"{username} :: {text}"
            await broadcaster.publish(formatted_message)
    except WebSocketDisconnect:
        await broadcaster.unsubscribe(ws)
        await broadcaster.publish(f"client {client_id} ({username}) unsubscribed from {chat_name}")
        if not broadcaster.subscribers:
            del chat_broadcasters[chat_name]

