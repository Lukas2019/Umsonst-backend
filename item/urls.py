from django.urls import path, include

from .views import (
    ItemPictureView,
    MyItemView,
    ShareCircleInfoView,
    ShareCircleSearchView,
    CitySearchView,
    ShareCircleItemsView,
    ShareCircleView,
    ApiVersionView,
    ItemView,
    ShareCircleJoinView,
    ShareCircleLeaveView,
    ShareCircleFeedView,
    ShareCircleJoinPostView,
    ShareCircleLeavePostView,
    PosterInAnyShareCircleView,
    FlagItemView,
    ShareCircleJoinPostLocationView
)
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

app_name = 'item'

urlpatterns = [
    path('sharecircle/', ShareCircleSearchView.as_view(), name='sharecircle-search'),
    path('city/', CitySearchView.as_view(), name='city-search'),
    #path('sharecircle/by-city/', ShareCircleCitySearchView.as_view(), name='sharecircle-city-search'),
    path('sharecircle/my-feed/', ShareCircleFeedView.as_view(), name='my-feed'),
    path('sharecircle/is-poster/', PosterInAnyShareCircleView.as_view(), name='poster-in-sharecircle'),
    path('sharecircle/join-post-location/', ShareCircleJoinPostLocationView.as_view(), name='join-as-poster-location'),
    path('sharecircle/<slug:pk>/', ShareCircleView.as_view(), name='sharecircle-info'),
    path('sharecircle/<slug:slug>/items/', ShareCircleItemsView.as_view(), name='sharecircle-items'),
    path('sharecircle/<slug:slug>/join/', ShareCircleJoinView.as_view(), name='join-circle'),
    path('sharecircle/<slug:slug>/leave/', ShareCircleLeaveView.as_view(), name='leave-circle'),
    path('sharecircle/<slug:slug>/join-post/', ShareCircleJoinPostView.as_view(), name='join-as-poster'),
    path('sharecircle/<slug:slug>/leave-post/', ShareCircleLeavePostView.as_view(), name='leave-as-poster'),
    path('item/<uuid:pk>/flag/', FlagItemView.as_view(), name='flag-item'),
    path('api-version/', ApiVersionView.as_view(), name='test'),
    # path('',APIDokumentation.as_view(), name='api'),
    path('item/<slug:pk>/', ItemView.as_view(), name='post'),
]

router = routers.SimpleRouter()
router.register(r'my-item', MyItemView, basename='my-item')
router.register(r'image', ItemPictureView, basename='Image')
# router.register(r'sharecircle',ShareCircleInfoView,
#                basename='sharecircle-info')
# router.register(r'sharecircle/search',ShareCircleSearchView,basename='sharecircle-search')


urlpatterns += router.urls
