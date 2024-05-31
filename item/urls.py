from django.urls import path, include
from .views import (
    ItemPictureView,
    ItemView,
    ShareCircleInfoView,
    ItemsInShareCircleView
)
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'post', ItemView, basename='post' )
router.register(r'post-image', ItemPictureView, basename='Image')
router.register(r'sharecircle-info',ShareCircleInfoView,
                basename='sharecircle-info')
#   
router.register(r'sharecirc-posts/<slug:slug>/',ItemsInShareCircleView,basename='sharecirc-posts')


urlpatterns = router.urls
