# god doku https://blog.logrocket.com/django-rest-framework-build-an-api-in-15-minutes/
from rest_framework import status, permissions, viewsets, mixins
from item.models import Item, ItemPictures, ShareCircle

from .serializers import (PostSerializer,
                          PicturesSerializer,
                          ShareCircleInfoSerializer,
                          PostSerializerAdmin,
                          ItemsInShareCircleView)
from rest_framework.response import Response
from .permissions import (IsOwnerPermission,
                          IsSharCircleAdminPermission,
                          Variant,)

class ItemPictureView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    #http_method_names = ['POST', 'OPTIONS']
    permission_classes = [permissions.IsAuthenticated]
    queryset = ItemPictures.objects.all()
    serializer_class = PicturesSerializer


    def get_queryset(self):
        id = self.request.user.id
        return ItemPictures.objects.filter(
            forItems__sharecircle__user__exact=id)

    def get_permissions(self):
        #deny on change and deled
        ac = self.action
        if ac == 'update' or ac == 'partial_update':
            return [IsOwnerPermission(Variant.ItemPicture)]
        else:
            return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        return Response({'detail': 'use /post-image/<id>/ to access an '
                                    'image or to '
                            'change it'})

# main feed
class ItemView(viewsets.ModelViewSet):
    # shows all items some on is allowed to
    permission_classes = [permissions.IsAuthenticated]
    #serializer_class = PostSerializer
    #queryset = Item.objects.all()
    admin = False

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.admin:
            return PostSerializerAdmin
        else:
            return PostSerializer

    def get_permissions(self):
        self.admin = IsSharCircleAdminPermission(Variant.Item)

        ac = self.action
        if ac == 'update' or ac == 'partial_update':
            return [IsOwnerPermission(Variant.Item)]
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        id = self.request.user.id
        query = Item.objects.filter(
             user__id=id).all()
        return query
    

    def only_allowed_flag(self, request, serializer):
        id = request.user.id
        sharecircle_flagged = serializer.data['flagged']
        for sharecircle_id in sharecircle_flagged:
            if not ShareCircle.objects.filter(user__exact=id)\
                .filter(id__exact=sharecircle_id).exists():
                serializer.data['flagged'].remove(sharecircle_id)
        return serializer

    def validated_data(self):
        pass

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer = self.only_allowed_flag(request, serializer)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    # def perform_create(self, serializer):
    #     serializer.save()


class ShareCircleInfoView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShareCircleInfoSerializer
    def get_queryset(self):
        id = self.request.user.id
        return ShareCircle.objects.filter(user__id__exact=id)
    
class ItemsInShareCircleView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ItemsInShareCircleView

    def get_queryset(self):
        item = self.kwargs['slug']
        return Item.objects.filter(sharecircle__exact=item).all()
