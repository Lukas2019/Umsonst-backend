from django.urls import path
from . import views
from django.urls import re_path
from . import consumers

app_name = 'chat'

urlpatterns = [
    path('', views.ChatsView.as_view(), name='chat-view'),
    path("ws/", views.index, name="index"),
    path("ws/<str:room_name>/", views.room, name="room"),
    path('message/<slug:slug>/', views.MessageView.as_view(), name='message-create-view'),
    path('unread_count/', views.UnreadMessagesCountView.as_view(), name='unread-messages-count-view'),
    path('unread_count/<slug:slug>/', views.UnreadMessagesChatCountView.as_view(), name='unread-messages-count-view'),
    path('unread/<slug:slug>/', views.LastUnreadMessageView.as_view(), name='unread-messages-view'),
    path('read/<slug:slug>/', views.ReadMessagesView.as_view(), name='read-messages-view'),
    path('by_user/<slug:slug>/', views.ChatByUserView.as_view(), name='chat-by-user-view'),
    path('<slug:slug>/', views.MessageView.as_view(), name='message-view'),
]
