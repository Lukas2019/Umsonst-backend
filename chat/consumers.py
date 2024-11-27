import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Chat, Message
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)

class UnreadMessagesCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]
            
            if self.user.is_anonymous:
                logger.warning("Anonymous user attempted to connect")
                await self.close()
                return
                
            try:
                self.room_name = self.scope['url_route']['kwargs']['room_name']
            except KeyError:
                logger.error("Missing room_name parameter")
                await self.close()
                return

            self.room_group_name = f"user_{self.user.id}_unread_messages"

            # First accept the connection
            await self.accept()

            # Then join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Finally send initial unread count
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'unread_count': unread_count,
                'chat_id': self.room_name
            }))
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            if self.accepted:
                await self.close()

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

    @database_sync_to_async
    def get_unread_count(self):
        try:
            return Message.objects.filter(
                chat__id=self.room_name,
                read=False
            ).exclude(user=self.user).count()
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return 0


class UnreadMessagesGeneralCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"user_{self.user.id}_general_unread_messages"

            await self.accept()

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Send initial unread count
            """
            unread_count = await self.get_unread_count(self.user)
            await self.send(text_data=json.dumps({
                'unread_count': unread_count,
            }))
            """

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_general_unread_count(self, event):
        unread_count = event['unread_count']
        await self.send(text_data=json.dumps({
            'unread_count': unread_count,
        }))

    @database_sync_to_async
    def get_unread_count(self, user):
        return Message.objects.filter(
            Q(chat__user1=user) | Q(chat__user2=user),
            read=False
        ).exclude(user=user).count()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        if self.user.is_anonymous:
            await self.close()
            return

        try:
            chat = await self.get_chat(self.room_name)
            if not await self.is_user_in_chat(chat, self.user):
                raise ValidationError("User is not part of the chat.")
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Mark messages as read when connecting
            await self.mark_messages_as_read()
            
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
        try:
            text_data_json = json.loads(text_data)
            content = text_data_json["content"]

            # Save message asynchronously
            message = await self.save_message(self.room_name, self.user, content)

            # Get other user's ID asynchronously
            other_user_id = await self.get_other_user_id(self.room_name, self.user.id)

            # Get updated unread count for the other user asynchronously
            unread_count = await self.get_unread_count_by_user_id(other_user_id)

            # Send message to chat room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'id': message.id.hex,
                    'userId': str(self.user.id),
                    'username': self.user.username,
                    'content': content,
                    'createdAt': message.created_at.isoformat()
                }
            )

            # Send updated unread count to the other user's group
            await self.channel_layer.group_send(
                f"user_{other_user_id}_general_unread_messages",
                {
                    'type': 'send_general_unread_count',
                    'unread_count': unread_count,
                }
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))

    async def send_general_unread_count(self, event):
        unread_count = event['unread_count']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'unread_count': unread_count,}))

    async def send_message(self, event):
        id = event["id"]
        userId = event["userId"]
        content = event["content"]
        username = event["username"]
        createdAt = event["createdAt"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'id': id,
            'content': content,
            'userId': userId,
            'username': username,
            'createdAt': createdAt
        }))

    @database_sync_to_async
    def mark_messages_as_read(self):
        Message.objects.filter(
            chat_id=self.room_name
        ).exclude(user=self.user).update(read=True)

    @database_sync_to_async
    def get_unread_count(self, user):
        return Message.objects.filter(
            Q(chat__user1=user) | Q(chat__user2=user),
            read=False
        ).exclude(user=user).count()

    @database_sync_to_async
    def get_chat(self, room_name):
        return Chat.objects.get(id=room_name)

    @database_sync_to_async
    def is_user_in_chat(self, chat, user):
        return user in [chat.user1, chat.user2]

    @database_sync_to_async
    def save_message(self, room_name, user, message):
        chat = Chat.objects.get(id=room_name)
        return Message.objects.create(chat=chat, user=user, text=message)

    @database_sync_to_async
    def get_other_user_id(self, room_name, current_user_id):
        try:
            chat = Chat.objects.get(id=room_name)
            if chat.user1_id == current_user_id:
                return chat.user2_id
            else:
                return chat.user1_id
        except Chat.DoesNotExist:
            raise ValidationError("Chat does not exist.")

    @database_sync_to_async
    def get_unread_count_by_user_id(self, user_id):
        return Message.objects.filter(
            Q(chat__user1_id=user_id) | Q(chat__user2_id=user_id),
            read=False
        ).exclude(user_id=user_id).count()