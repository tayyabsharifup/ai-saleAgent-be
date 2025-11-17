import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


class AsyncNotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token is None:
            await self.close()
            return

        try:
            untyped_token = UntypedToken(token)
            decoded_data = untyped_token.payload
            user_id = decoded_data['user_id']
            self.scope['user'] = await get_user(user_id)

            if self.scope['user'] is None:
                await self.close()
                return

        except (InvalidToken, TokenError):
            await self.close()
            return

        await self.accept()
        await self.send(text_data=json.dumps({"message": "Notification channel connected successfully!"}))

    async def receive(self, text_data=None, bytes_data=None):
        # This can be used for client-to-server communication if needed in the future.
        pass
