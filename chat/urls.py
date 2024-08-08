from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatsView.as_view(), name='chat-view'),
    path('message/<slug:slug>/', views.MessageView.as_view(), name='message-create-view'),
    path('unread/<slug:slug>/', views.LastUnreadMessagesView.as_view(), name='unread-messages-view'),
    # path('by_user/<slug:slug>/', views.ChatByUserView.as_view(), name='chat-by-user-view'),
    path('<slug:slug>/', views.MessageView.as_view(), name='message-view'),

]