from django.shortcuts import render
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from .models import Chat, Message
from user.models import User
from .serializers import ChatSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class ChatsView(ListCreateAPIView):
    #queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user1 = request.user
            user2 = serializer.validated_data.get('user2')
            if user1.id.hex == user2.id.hex:
                return Response({'error': 'You cannot create a chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
            chat, created = Chat.objects.get_or_create(
                user1=User.objects.get(id=min(user1.id, user2.id, key=lambda user: user.int)),
                user2=User.objects.get(id=max(user1.id, user2.id, key=lambda user: user.int)),
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

class MessageView(ListCreateAPIView):
    #queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(chat=self.kwargs['slug'])

    def perform_create(self, serializer):
        user = self.request.user
        chat = Chat.objects.get(id=self.kwargs['slug'])
        # Set the user for the message to the current user
        serializer.save(user=user, chat=chat)