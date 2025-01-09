# god doku https://blog.logrocket.com/django-rest-framework-build-an-api-in-15-minutes/
import dis

from django.db.models import Q
from pyasn1_modules.rfc5280 import id_at_initials
from rest_framework.exceptions import APIException
from django.urls import reverse
from rest_framework import status, filters, permissions, generics, viewsets, mixins
from item.models import City, Item, ItemPictures, ShareCircle
from rest_framework.views import APIView
from um_be.email_utils import send_html_mail
from user.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.template.loader import render_to_string
from firebase_admin.messaging import Message as FCMMessage, Notification
from fcm_django.models import FCMDevice

from .serializers import (PostSerializer,
                          PicturesSerializer,
                          ShareCircleInfoSerializer,
                          PostSerializerAdmin,
                          ItemSerializer, CitySearchSerializer, )
from rest_framework.response import Response
from .permissions import (IsOwnerPermission,
                          IsSharCircleAdminPermissionItem,
                          Variant,)
from rest_framework.decorators import action
import requests
from django.conf import settings

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


class ApiVersionView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Wenn der Benutzer authentifiziert ist, wird eine positive Antwort zurückgegeben
        return Response({"api-version": "0.0.1"})


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
    serializer_class = PostSerializer
    #queryset = Item.objects.all()
    admin = False

    def perform_create(self, serializer):
        if self.request.user.post_circle == None:
            raise CustomValidationError('Du musst einen HomeCircle beitreten')
        share_circle = self.request.user.post_circle
        serializer.save(user=self.request.user, sharecircle=[share_circle])
        content = serializer.data['title']
        user_ids = User.objects.filter(item_notifications=True).values_list('id', flat=True)
        other_user_id = share_circle.user.all().exclude(id=self.request.user.id).filter(id__in=user_ids)

        # Send push notification to all users
        devices = FCMDevice.objects.filter(user__in=other_user_id)
        devices.send_message(FCMMessage(
            notification=Notification(
                title=f"Neue Anzeige",
                body=f"{content}"
            ),
        ))

    '''
    def get_serializer_class(self):
        self.admin = ShareCircle.objects.filter(admin__exact=self.request.user.id, id__exact=self.kwargs['pk']).exists()
        if self.admin:
            return PostSerializerAdmin
        else:
            return PostSerializer
    '''
    def get_permissions(self):

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


class FlagItemView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsSharCircleAdminPermissionItem]

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        # Deaktiviere den User wenn er zwei flaggs hat
        user = item.user
        if Item.objects.filter(user = user, flagged=True).count() >= 2:
            user.is_active = False
            user.save()
            self.banned_email(user, item)
        else:
            self.waringEmail(user, item)
        item.flagged = True
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)
    
    def waringEmail(self, user, item):

        email_html = render_to_string('email/flaged_item_user_warning.html', {
            'title': item.title,
        })

        send_html_mail(
            "[Umsonst] Achtung: Artikel wurde gemeldet",
            email_html,
            [user.email],
        )

    def banned_email(self, user, item):

        email_html = render_to_string('email/user_banned.html', {
            'title': item.title,
        })

        send_html_mail(
            "[Umsonst] Sie wurden gesperrt",
            email_html,
            [user.email],
        )



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
            # Changed line:
            is_admin = sharecircle.admin.filter(id=request.user.id).exists()
            is_member = sharecircle.user.filter(id=request.user.id).exists()
            is_poster = sharecircle.poster.filter(id=request.user.id).exists()
            
            users = [user.id for user in sharecircle.user.all()]
            admins = [admin.id for admin in sharecircle.admin.all()]
            poster = [poster.id for poster in sharecircle.poster.all()]
            
            sharecircle_data = {
                'id': sharecircle.id,
                'title': sharecircle.title,
                'district': sharecircle.district,
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
        sharecircle = ShareCircle.objects\
            .filter(id__exact=kwargs['pk']).first()
        '''
        add is_admin and is_member to the response
        '''

        print(sharecircle)

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
        return Item.objects.filter(sharecircle__in=share_circles, flagged=False,is_active=True).all().order_by('-timestamp')

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
    
class ShareCircleJoinPostLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Extract coordinates
            data = request.data
            longitude = float(data.get('longitude'))
            latitude = float(data.get('latitude'))
            
            # Validate coordinates
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                return Response(
                    {"detail": "Invalid coordinate values"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Make HERE API request
            api_key = settings.HERE_API_KEY
            url = "https://revgeocode.search.hereapi.com/v1/revgeocode"
            params = {
                'at': f"{longitude},{latitude}",
                'lang': 'de-DE',
                'apiKey': api_key
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Extract location data
            location_data = response.json()
            if 'items' in location_data and location_data['items']:
                location = location_data['items'][0]['address'].get('city', '')
                district = location_data['items'][0]['address'].get('district', '')
                if district == location:
                    district = 'Kernstadt'
                
                if not location:
                    return Response(
                        {"detail": "No city found for these coordinates"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {"detail": f"Location data not found {location_data} {params}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Update user location
            user = request.user
            user.longitude = longitude
            user.latitude = latitude
            user.country = location_data['items'][0]['address'].get('countryName', '')
            user.zipcode = location_data['items'][0]['address'].get('postalCode', '')
            user.city = location
            user.street = location_data['items'][0]['address'].get('street', '')
            # user.house_number = location_data['items'][0]['address'].get('houseNumber', '')
            user.save()

            # Handle share circle
            city, created = City.objects.get_or_create(
                name=location
            )
            share_circle, created = ShareCircle.objects.get_or_create(
                district=f"{district}".strip(),
                city=city
            )
            # Add admin user if share circle was created
            if created:
                share_circle.description = f"ShareCircle für {location} {district}"
                share_circle.admin.add(User.objects.get(is_superuser=True))
                share_circle.user.add(User.objects.get(is_superuser=True))
                share_circle.save()

            # Remove user from previous share circle if exists
            if ShareCircle.objects.filter(poster=user).exists():
                old_circle = ShareCircle.objects.filter(poster=user).first()
                old_circle.poster.remove(user)

            # Add user to new share circle
            share_circle.poster.add(user)
            share_circle.user.add(user)
            share_circle.save()

            return Response({
                "detail": "Successfully updated location and share circle",
                "location": location,
                "district": district,
                "coordinates": {
                    "longitude": longitude,
                    "latitude": latitude
                }
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {"detail": "Invalid coordinate format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except requests.RequestException as e:
            return Response(
                {"detail": f"Error fetching location data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
        if ShareCircle.objects.filter(poster__id=request.user.id).exists():
            is_in_share_circle = ShareCircle.objects.filter(poster__id=request.user.id).first().id
            return Response({'poster_in_share_circle': is_in_share_circle})
        else:
            return Response({'poster_in_share_circle': None})
        

class CitySearchView(generics.ListAPIView):
    serializer_class = CitySearchSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name', 'sharecircle__district']
    queryset = City.objects.all()
    page_size = 40
    paginate_by = 40