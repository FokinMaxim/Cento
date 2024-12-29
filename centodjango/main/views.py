from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from  .models import *
from .serializer import *
from rest_framework import viewsets, permissions, generics


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = StudentSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = TeacherSerializer

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = TariffSerializer

class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = VariantSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = TaskSerializer

class TypeOfTaskViewSet(viewsets.ModelViewSet):
    queryset = TypeOfTask.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = TypeOfTaskSerializer

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = ExamSerializer

class TeachersVariantStudentViewSet(viewsets.ModelViewSet):
    queryset = TeachersVariantStudent.objects.all()
    #permissions_classes = [
    #    permissions.AllowAny
    #]
    serializer_class = TeachersVariantStudentSerializer


class RegisterView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = RegisterSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer