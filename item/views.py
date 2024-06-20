# god doku https://blog.logrocket.com/django-rest-framework-build-an-api-in-15-minutes/
from django.urls import reverse
from rest_framework import status, filters, permissions, generics, viewsets, mixins
from item.models import Item, ItemPictures, ShareCircle

from .serializers import (PostSerializer,
                          PicturesSerializer,
                          ShareCircleInfoSerializer,
                          PostSerializerAdmin,
                          ItemsInShareCircleSerializer,)
from rest_framework.response import Response
from .permissions import (IsOwnerPermission,
                          IsSharCircleAdminPermission,
                          Variant,)
from rest_framework.decorators import action
from django.views.generic import TemplateView


class APIDokumentation(TemplateView):
    template_name = 'api.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context = super().get_context_data(**kwargs)
        context['urls'] = [
            reverse('questions'),
            reverse('sharecircle-info', args=['slug']),
            reverse('sharecircle-items', args=['slug']),
            reverse('api'),
            reverse('post', args=['slug']),
            reverse('my-item-list'),
            reverse('Image-list')
            ]


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
class MyItemView(viewsets.ModelViewSet):
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

class ItemView(generics.RetrieveAPIView):
    serializer_class = PostSerializer
    queryset = Item.objects.all()


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
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, admin=self.request.user)
    
    def perform_update(self, serializer):
        # Prüft, ob der Benutzer ein Admin des ShareCircle ist
        if not ShareCircle.objects.filter(admin__exact=self.request.user.id)\
            .filter(id__exact=serializer.instance.id).exists():
            return Response({"detail": "You are not an admin of this ShareCircle"},
                           status=status.HTTP_403_FORBIDDEN)
        serializer.save()
    
    @action(detail=True, methods=['GET'])
    def items(self, request, pk=None):
        """
        Benutzerdefinierte Aktion für ein einzelnes Item.
        Beispiel-URL: /sharecircle-info/<pk>/items/
        """
        # Führe hier deine benutzerdefinierte Logik aus
        list_of_items= Item.objects.filter(sharecircle__exact=pk).filter(is_active=True).all()
        # Prüfe, ob der Benutzer user im ShareCircle ist
        if not ShareCircle.objects.filter(user__exact=request.user.id)\
            .filter(id__exact=pk).exists():
            return Response({"detail": "You are not in this ShareCircle"},
                           status=status.HTTP_403_FORBIDDEN)
        serializer = ItemsInShareCircleSerializer(list_of_items, many=True)
        return Response(serializer.data)
    

class ShareCircleSearchView(generics.ListCreateAPIView):
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    queryset = ShareCircle.objects.all()
    serializer_class = ShareCircleInfoSerializer


class ShareCircleItemsView(generics.ListAPIView):
    serializer_class = ItemsInShareCircleSerializer
    search_fields = ['title', 'description']
    filter_backends = (filters.SearchFilter,)


    def get_queryset(self):
        slug = self.kwargs['slug']
        return Item.objects.filter(sharecircle__exact=slug).all()
    
class ShareCircleView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShareCircleInfoSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return ShareCircle.objects.filter(id__exact=pk).all()

    def put(self, request, *args,
            
            
             **kwargs):
        if not ShareCircle.objects.filter(admin__exact=self.request.user.id)\
            .filter(id__exact=kwargs['pk']).exists():
            return Response({"detail": "You are not an admin of this ShareCircle"},
                           status=status.HTTP_403_FORBIDDEN)
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not ShareCircle.objects.filter(admin__exact=self.request.user.id)\
            .filter(id__exact=kwargs['pk']).exists():
            return Response({"detail": "You are not an admin of this ShareCircle"},
                           status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not ShareCircle.objects.filter(admin__exact=self.request.user.id)\
            .filter(id__exact=kwargs['pk']).exists():
            return Response({"detail": "You are not an admin of this ShareCircle"},
                           status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)
