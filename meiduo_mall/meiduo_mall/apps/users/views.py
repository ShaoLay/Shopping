from django.shortcuts import render
from rest_framework.generics import CreateAPIView

# Create your views here.
from users import serializers


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = serializers.CreateUserSerializer
