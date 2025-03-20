from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from ..serializer import *


class RegisterView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = RegisterSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer