from .models import ItemPictures, Item, ShareCircle, City
from user.models import User
from rest_framework import serializers


# #Post
# post-image/
class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPictures
        fields = '__all__'

# post/
class PicturesSerializerForPost(serializers.ModelSerializer):
    class Meta:
        model = ItemPictures
        fields = ['id']#('itemPicture', 'id')

# #Share circle
# sharecircle-info
class ShareCircleInfoSerializer(serializers.ModelSerializer):
    # user = UserIDSerializer(read_only=False,many=True,)
    #id = serializers.
    class Meta:
        model = ShareCircle
        fields = ['id',  'description', 'title', 'admin', 'user']
        #depth = 2

# #City

class ShareCircleTitleSerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = ShareCircle
        fields = ['district', 'id', 'is_member']

    def get_is_member(self, obj):
        user = self.context['request'].user
        return obj.is_member(user)

# city-search
class CitySearchSerializer(serializers.ModelSerializer):
    sharecircle_set = ShareCircleTitleSerializer(many=True, read_only=True)
    class Meta:
        model = City
        fields = ['name', 'id', 'sharecircle_set']


class PostSerializer(serializers.ModelSerializer):
    images = PicturesSerializerForPost(read_only=True, many=True, )
    sharecircle = ShareCircleInfoSerializer(read_only=True, many=True,)
    #user = serializers.HiddenField(
    # default=serializers.CurrentUserDefault(),)
    class Meta:
        model = Item
        fields = ['title', 'description', 'type', 'itemID',
                  'sharecircle', 'user', 'reserved', 
                  'images', 'is_active', 'timestamp', 'updated', 'flagged']
        extra_kwargs = {
            'flagged': {'read_only': True},
            'timestamp': {'read_only': True},
            'updated': {'read_only': True},
            'user': {'read_only': True},
            #'sharecircle': {'read_only': True},
        }

class PostSerializerAdmin(PostSerializer):
    class Meta(PostSerializer.Meta):
        extra_kwargs = {
            'timestamp': {'read_only': True},
            'updated': {'read_only': True},
            'user': {'read_only': True}
        }


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'  # Include all fields or specify the ones you need
        read_only_fields = ['flagged']
