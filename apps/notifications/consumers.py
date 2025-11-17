import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AsyncNotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'notifications_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({"message": f"Connected to notifications for user {self.user.first_name}!"}))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                msg = data.get("message", "")
                # Example of echoing the message back to the user
                await self.send(text_data=json.dumps({"reply": f"You said: {msg}"}))
            except json.JSONDecodeError:
                await self.send(text_data=json.dumps({"error": "Invalid JSON"}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
