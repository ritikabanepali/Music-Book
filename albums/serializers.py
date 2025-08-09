from django.contrib.auth.models import User # the default user object
from rest_framework import serializers # provides the tools to convert complex data types into python data types

class UserRegisterSerializer(serializers.ModelSerializer): # generates serializer fields and validators based on a Django model
    password = serializers.CharField(write_only=True) # adds a password field to the serializer

    class Meta:
        model = User # configuration for the model serializer
        fields = ('username', 'password', 'email') # This specifies which fields from the User model should be included in the serializer for processing

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user
