from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatsView.as_view(), name='chat-view'),
    path('<slug:slug>/', views.MessageView.as_view(), name='message-view'),
    path('message/', views.MessageView.as_view(), name='message-create-view'),
]