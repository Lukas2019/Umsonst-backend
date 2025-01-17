from os import read
from django.shortcuts import render
from django.db.models import Max
from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView, GenericAPIView
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message as FCMMessage, Notification

from item.models import ShareCircle
from .models import Chat, Message
from user.models import Complaint, User
from .serializers import ChatSerializer, MessageSerializer,MessageCreateSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# Create your views here.
class ChatsView(ListCreateAPIView):
    #queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        chat = Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)
        return chat.annotate(last_message_date=Max('messages__created_at')).order_by('-last_message_date')
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user1 = request.user
            user2 = serializer.validated_data.get('user2')
            item = serializer.validated_data.get('item')
            if user1.id.hex == user2.id.hex:
                return Response({'error': 'You cannot create a chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
            chat, created = Chat.objects.get_or_create(
                user1=User.objects.get(id=min(user1.id, user2.id, key=lambda user: user.int)),
                user2=User.objects.get(id=max(user1.id, user2.id, key=lambda user: user.int)),
                item=item
            )
            if created:
                #serializer.save()
                json = {'id': chat.id}
                return Response(json, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Chat already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    '''
    def perform_create(self, serializer):
        user1 = self.request.user
        user2 = serializer.validated_data.get('user2')  # Angenommen, 'user2' ist im Serializer definiert

        # Überprüfen, ob ein Chat zwischen diesen zwei Benutzern bereits existiert
        if user1.id.hex != user2.id.hex:
            chat, created = Chat.objects.get_or_create(
                user1=min(user1.id, user2.id, key=lambda user: user.int),
                user2=max(user1.id, user2.id, key=lambda user: user.int),
            )
        else:
            json = {'error': 'You cannot create a chat with yourself'}
            return Response(json, status=status.HTTP_400_BAD_REQUEST)

        if created:
            serializer.save()
        else:
            # returns an error response
            json = {'error': 'Chat already exists'}
            return Response(json, status=status.HTTP_400_BAD_REQUEST)
    '''

class twentySetPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'next': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.page.previous_page_number() if self.page.has_previous() else None,
            'count': self.page.paginator.count,
            'pages': self.page.paginator.count//self.page_size + 1,
            'results': data
        })

class MessageView(ListCreateAPIView):
    #queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = twentySetPagination


    def get_queryset(self):
        return Message.objects.filter(chat=self.kwargs['slug']).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        user_name = user.username if user.username else user.email
        chat = Chat.objects.get(id=self.kwargs['slug'])
        user2 = chat.user1 if chat.user1 != user else chat.user2
        # You can still use .filter() or any methods that return QuerySet (from the chain)
        device = FCMDevice.objects.filter(user=user2).all()
        # send_message parameters include: message, dry_run, app
        device.send_message(FCMMessage(
            notification=Notification(title=f"Neue Nachricht von {user_name}", body=self.request.data['text'], image="url"),
        ))
        # Set the user for the message to the current user
        serializer.save(user=user, chat=chat)

        

class ChatByUserView(ListAPIView):
    #queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        user2 = User.objects.get(id=self.kwargs['slug'])
        chat = Chat.objects.filter(user1=user).filter(user2=user2) | Chat.objects.filter(user2=user).filter(user1=user2)
        return chat.annotate(last_message_date=Max('messages__created_at')).order_by('-last_message_date')

class ChatByItemUserView(ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        item = self.kwargs['item']
        user = self.request.user
        user2 = User.objects.get(id=self.kwargs['user'])
        chat = Chat.objects.filter(item=item).filter(Q(user1=user, user2=user2) | Q(user1=user2,user2=user))
        return chat.annotate(last_message_date=Max('messages__created_at')).order_by('-last_message_date')


class LastUnreadMessageView(GenericAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        id = self.kwargs['slug']
        user = self.request.user
        return Message.objects.filter(chat__id=id).exclude(user=user).filter(read=False).order_by('created_at').first()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)


class UnreadMessagesChatCountView(GenericAPIView):
    def get_queryset(self):
        id = self.kwargs['slug']
        user = self.request.user
        if hasattr(user, '_wrapped'):
            user = user._wrapped
        return Message.objects.filter(chat__id=id).exclude(user=user).filter(read=False)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        unread_count = queryset.count()
        return Response({'unread_count': unread_count})
        
class UnreadMessagesCountView(GenericAPIView):
    def get_queryset(self):
        share_circle_admin = ShareCircle.objects.filter(admin=self.request.user)
        user = self.request.user
        if hasattr(user, '_wrapped'):
            user = user._wrapped
        chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))
        complaints = Complaint.objects.filter(user__post_circle__in=share_circle_admin)
        return chats, complaints

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if hasattr(user, '_wrapped'):
            user = user._wrapped
        chats, complaints = self.get_queryset()
        print(complaints)
        unread_count = 0

        # Count unread messages in chats
        for chat in chats:
            unread_count += Message.objects.filter(chat=chat).exclude(user=user).filter(read=False).count()

        # Count unread messages in complaints

        unread_count += Complaint.objects.filter(user__post_circle__admin=user, read=False).count()

        return Response({'unread_count': unread_count})


class ReadMessagesView(GenericAPIView):
    serializer_class = MessageCreateSerializer

    def create(self, request, *args, **kwargs):
        id = self.kwargs['slug']
        user = request.user
        if hasattr(user, '_wrapped'):
            user = user._wrapped
        messages = Message.objects.filter(chat__id=id).exclude(user=user).filter(read=False)
        for message in messages:
            message.read = True
            message.save()
        return Response(status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
