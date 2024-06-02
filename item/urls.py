from django.urls import path, include
from .views import (
    ItemPictureView,
    ItemView,
    ShareCircleInfoView,
)
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

router = routers.DefaultRouter() #trailing_slash=False)
router.register(r'post', ItemView, basename='post' )
router.register(r'post-image', ItemPictureView, basename='Image')
router.register(r'sharecircle-info',ShareCircleInfoView,
                basename='sharecircle-info')




urlpatterns = router.urls
