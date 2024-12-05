from user.models import User, Complaint
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'is_admin', 'is_superuser', 'is_active', 'is_freezed', 'is_staff', )
        read_only_fieled = ['id', 'last_login', 'date_joined', 'is_admin', 'is_superuser', 'is_active', 'is_freezed', 'is_staff', 'username',]

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['id', 'date', 'read']