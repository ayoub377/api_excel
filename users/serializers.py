from django.contrib.auth.models import Group, User
from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "date_of_birth", "profile_picture", "address",
                  "username"]

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'],
                                   )
        user.set_password(validated_data['password'])
        user.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
