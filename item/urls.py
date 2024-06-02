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

router = routers.DefaultRouter() #trailing_slash=False)
router.register(r'post', ItemView, basename='post' )
router.register(r'post-image', ItemPictureView, basename='Image')
router.register(r'sharecircle-info',ShareCircleInfoView,
                basename='sharecircle-info')
#   sharecirc-posts/9f5c0d38-351c-4075-97b2-8714d2b2de5a
router.register('sc/(?P<slug>[^/.]+)',ItemsInShareCircleView,basename='sharecirc-posts1')
router.register("sh/x{5}",ItemsInShareCircleView,basename='sharecirc-posts2')



urlpatterns = router.urls
