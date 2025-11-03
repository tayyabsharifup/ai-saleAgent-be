import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class AsyncNotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected to new world!"}))
        asyncio.create_task(self.send_hello_world())

    async def send_hello_world(self):
        await asyncio.sleep(10)
        await self.send(text_data=json.dumps({"message": "hello world"}))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                msg = data.get("message", "")
                await self.send(text_data=json.dumps({"message": f"You said: {msg}"}))
            except json.JSONDecodeError:
                await self.send(text_data=json.dumps({"error": "Invalid JSON"}))