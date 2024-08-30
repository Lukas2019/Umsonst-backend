'''
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message

class UnreadMessagesCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f"user_{self.user.id}_unread_messages"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Berechnen der ungelesenen Nachrichten
        unread_count = await self.get_unread_messages_count()

        # Senden der ungelesenen Nachrichten an den WebSocket
        await self.send(text_data=json.dumps({
            'unread_count': unread_count
        }))

    async def get_unread_messages_count(self):
        user = self.user
        chats = Chat.objects.filter(user1_id=user) | Chat.objects.filter(user2_id=user)
        unread_count = 0
        for chat in chats:
            unread_count += Message.objects.filter(chat=chat).exclude(user=user).filter(read=False).count()
        return unread_count

        '''