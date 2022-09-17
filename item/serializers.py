from .models import ItemPictures, Item, ShareCircle
from user.models import Users
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
        fields = ('itemPicture', 'id')

class PostSerializer(serializers.ModelSerializer):
    images = PicturesSerializerForPost(read_only=True, many=True, )
    #user = serializers.HiddenField(
    # default=serializers.CurrentUserDefault(),)
    class Meta:
        model = Item
        fields = ['title', 'description', 'type', 'category', 'itemID',
                  'item_size', 'sharecircle', 'user', 'longitude', 'latitude',
                  'images', 'is_active', 'timestamp', 'updated', 'flagged']
        extra_kwargs = {
            'flagged': {'read_only': True},
            'timestamp': {'read_only': True},
            'updated': {'read_only': True},
            'user': {'read_only': True}
        }

class PostSerializerAdmin(PostSerializer):
    class Meta(PostSerializer.Meta):
        extra_kwargs = {
            'timestamp': {'read_only': True},
            'updated': {'read_only': True},
            'user': {'read_only': True}
        }

# #Share circle
# sharecircle-info
class ShareCircleInfoSerializer(serializers.ModelSerializer):
    # user = UserIDSerializer(read_only=False,many=True,)
    #id = serializers.
    class Meta:
        model = ShareCircle
        fields = ['id', 'title', 'description', 'user', 'admin', 'user',]
        #depth = 2
