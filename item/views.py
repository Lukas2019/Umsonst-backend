# god doku https://blog.logrocket.com/django-rest-framework-build-an-api-in-15-minutes/
from rest_framework.exceptions import APIException
from django.urls import reverse
from rest_framework import status, filters, permissions, generics, viewsets, mixins
from item.models import Item, ItemPictures, ShareCircle
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (PostSerializer,
                          PicturesSerializer,
                          ShareCircleInfoSerializer,
                          PostSerializerAdmin,)
from rest_framework.response import Response
from .permissions import (IsOwnerPermission,
                          IsSharCircleAdminPermission,
                          Variant,)
from rest_framework.decorators import action
from django.views.generic import TemplateView

'''
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
'''

class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid data provided.'
    default_code = 'invalid'


class AuthenticatedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Wenn der Benutzer authentifiziert ist, wird eine positive Antwort zurückgegeben
        return Response({"status": "OK"})


class ItemPictureView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    #http_method_names = ['POST', 'OPTIONS']
    permission_classes = [permissions.IsAuthenticated]
    queryset = ItemPictures.objects.all()
    serializer_class = PicturesSerializer

    """
    def get_queryset(self):
        id = self.request.user.id
        return ItemPictures.objects.filter(
            forItems__sharecircle__user__exact=id)
    """
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
        if self.request.user.post_circle == None:
            raise CustomValidationError('Du musst einen HomeCircle beitreten')
        serializer.save(user=self.request.user, sharecircle=[self.request.user.post_circle])

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
             user__id=id).all().order_by('-timestamp')
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
    

class ShareCircleSearchView(generics.ListAPIView):
    queryset = ShareCircle.objects.all()
    serializer_class = ShareCircleInfoSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['title']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        paginator = self.pagination_class()
        paginated_sharecircles = paginator.paginate_queryset(queryset, request)
        
        response_data = []
        for sharecircle in paginated_sharecircles:
            is_admin = sharecircle.admin == request.user
            is_member = sharecircle.user.filter(id=request.user.id).exists()
            is_poster = sharecircle.poster.filter(id=request.user.id).exists()
            
            # Extract relevant fields of the users
            users = [user.id for user in sharecircle.user.all()]
            admins = [admin.id for admin in sharecircle.admin.all()]
            poster = [poster.id for poster in sharecircle.poster.all()]
            
            sharecircle_data = {
                'id': sharecircle.id,
                'title': sharecircle.title,
                'description': sharecircle.description,
                'users': users,
                'admins': admins,
                'poster': poster,
                'is_admin': is_admin,
                'is_member': is_member,
                'is_poster': is_poster,
            }
            response_data.append(sharecircle_data)
        
        return paginator.get_paginated_response(response_data)



class ShareCircleItemsView(generics.ListAPIView):
    serializer_class = PostSerializer
    search_fields = ['title', 'description']
    filter_backends = (filters.SearchFilter,)


    def get_queryset(self):
        slug = self.kwargs['slug']
        return Item.objects.filter(sharecircle__exact=slug).all().order_by('-timestamp')
    
class ShareCircleView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShareCircleInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShareCircle.objects.all()
    
    def get(self, request, *args, **kwargs):
        sharecircle = ShareCircle.objects.filter(user__exact=self.request.user.id)\
            .filter(id__exact=kwargs['pk']).first()
        '''
        add is_admin and is_member to the response
        '''

        is_admin = sharecircle.admin == request.user
        is_member = sharecircle.user.filter(id=request.user.id).exists()
        
        response = super().get(request, *args, **kwargs)
        response.data['is_admin'] = is_admin
        response.data['is_member'] = is_member 
        return response


    def put(self, request, *args, **kwargs):
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
    
class ShareCircleFeedView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    
    def get_queryset(self):
        share_circles = ShareCircle.objects.filter(user__exact=self.request.user.id).all()
        return Item.objects.filter(sharecircle__in=share_circles).all().order_by('-timestamp')

class ShareCircleJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        share_circle = ShareCircle.objects.get(pk=slug)
        if request.user in share_circle.user.all():
            return Response({"detail": "You are already a member of this ShareCircle"},
                            status=status.HTTP_400_BAD_REQUEST)
        share_circle.user.add(request.user)
        return Response({"detail": "You have successfully joined the ShareCircle"},
                        status=status.HTTP_200_OK)
    
class ShareCircleLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        share_circle = ShareCircle.objects.get(pk=slug)
        if request.user not in share_circle.user.all():
            return Response({"detail": "You are not a member of this ShareCircle"},
                            status=status.HTTP_400_BAD_REQUEST)
        share_circle.user.remove(request.user)
        return Response({"detail": "You have successfully left the ShareCircle"},
                        status=status.HTTP_200_OK)
    
class ShareCircleJoinPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        share_circle = ShareCircle.objects.get(pk=slug)
        if ShareCircle.objects.filter(poster=request.user).exists():
            leav_circle = ShareCircle.objects.filter(poster=request.user).first().id
            ShareCircle.objects.get(pk=leav_circle).poster.remove(request.user)
        share_circle.poster.add(request.user)
        return Response({"detail": "Du bist dem ShareCircle beigetreten"},
                        status=status.HTTP_200_OK)
    
class ShareCircleLeavePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        share_circle = ShareCircle.objects.get(pk=slug)
        if request.user not in share_circle.poster.all():
            return Response({"detail": "You are not a member of this ShareCircle"},
                            status=status.HTTP_400_BAD_REQUEST)
        share_circle.poster.remove(request.user)
        return Response({"detail": "You have successfully left the ShareCircle"},
                        status=status.HTTP_200_OK)
    
class PosterInAnyShareCircleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        is_in_share_circle = ShareCircle.objects.filter(poster__id=request.user.id).exists()
        return Response({'poster_in_share_circle': is_in_share_circle})
    