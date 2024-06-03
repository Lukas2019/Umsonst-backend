from django.urls import path, include

from .views import (
    ItemPictureView,
    ItemView,
    ShareCircleInfoView,
    ShareCircleSearchView,
)
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

urlpatterns = [
    path('sharecircle/search/',ShareCircleSearchView.as_view(), name='questions'),
    ]

router = routers.SimpleRouter(trailing_slash=False) #trailing_slash=False)
router.register(r'post', ItemView, basename='post' )
router.register(r'post-image', ItemPictureView, basename='Image')
router.register(r'sharecircle',ShareCircleInfoView,
                basename='sharecircle-info')
#router.register(r'sharecircle/search',ShareCircleSearchView,basename='sharecircle-search')



urlpatterns += router.urls
