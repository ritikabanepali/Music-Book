from django.shortcuts import render
from rest_framework import generics # provides pre-built, reusable views that handle common patterns, like creating objects or listing objects
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer # knows how to validate registration data and create a new User securely
from rest_framework.permissions import IsAuthenticated

class RegisterView(generics.CreateAPIView): # This generic view is specifically designed to handle POST requests for creating a new object instance
    queryset = User.objects.all() # what set of objects CreatAPIView is working with
    serializer_class = UserRegisterSerializer

# The CreateAPIView will automatically use this serializer to:
#   Validate the incoming POST request data.
#   Call the serializer's .create() method (customized to hash the password) to save the new User object to the database.

class ReviewCreateView(generics.CreateAPIView):
    # Review model & serializer 
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # link review to logged-in user