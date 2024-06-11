from django.urls import path, include

from .views import (
    ItemPictureView,
    MyItemView,
    ShareCircleInfoView,
    ShareCircleSearchView,
    ShareCircleItemsView,
    ShareCircleView,
    ItemView,
    APIDokumentation
)
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

app_name = 'item'

urlpatterns = [
    path('sharecircle/',ShareCircleSearchView.as_view(), name='questions'),
    path('sharecircle/<slug:pk>/',ShareCircleView.as_view(), name='sharecircle-info'),
    path('sharecircle/<slug:slug>/items/',ShareCircleItemsView.as_view(), name='sharecircle-items'),
    path('',APIDokumentation.as_view(), name='api'),
    path('item/<slug:pk>/',ItemView.as_view(), name='post')
    ]

router = routers.SimpleRouter()
router.register(r'my-item', MyItemView, basename='my-item' )
router.register(r'post-image', ItemPictureView, basename='Image')
#router.register(r'sharecircle',ShareCircleInfoView,
#                basename='sharecircle-info')
#router.register(r'sharecircle/search',ShareCircleSearchView,basename='sharecircle-search')



urlpatterns += router.urls
