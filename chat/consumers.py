import json
from math import e
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError
from .models import Chat, Message
from channels.db import database_sync_to_async

class UnreadMessagesCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
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
        # This method can be used to handle messages received from the WebSocket
        pass

    async def send_unread_count(self, event):
        unread_count = event['unread_count']
        chat_id = event['chat_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'unread_count': unread_count,
            'chat_id': chat_id
        }))


class UnreadMessagesGeneralCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"user_{self.user.id}_general_unread_messages"

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
        # This method can be used to handle messages received from the WebSocket
        pass

    async def send_general_unread_count(self, event):
        unread_count = event['unread_count']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'unread_count': unread_count,
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Überprüfen, ob der Benutzer authentifiziert ist
        if self.user.is_anonymous:
            await self.close()
        else:
            try:
                # Überprüfen, ob die Chat-ID gültig ist und der Benutzer Teil des Chats ist
                chat = await self.get_chat(self.room_name)
                if not await self.is_user_in_chat(chat, self.user):
                    raise ValidationError("User is not part of the chat.")
                
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                await self.accept()
            except (Chat.DoesNotExist, ValidationError) as e:
                print(f"Connection rejected: {e}")
                await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_message',
                'user': self.user.id.hex,
                'message': message,
            }
        )

    async def send_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_chat(self, room_name):
        return Chat.objects.get(id=room_name)

    @database_sync_to_async
    def is_user_in_chat(self, chat, user):
        return user in [chat.user1, chat.user2]