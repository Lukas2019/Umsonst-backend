
import json
from channels.generic.websocket import AsyncWebsocketConsumer

import user


from .models import Chat, Message
import json
from channels.generic.websocket import WebsocketConsumer

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
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"{self.scope['url_route']['kwargs']['room_name']}"
            print(f"\"{self.room_group_name}\"")
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
    
    async def send_message(self, event):
        message = event["message"]
        user_id = event["user_id"]
        print("send_message", message)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message, 
            "user_id": user_id
            }))