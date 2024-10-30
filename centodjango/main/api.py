from .models import Student
from  rest_framework import  viewsets, permissions
from .serializer import  StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = StudentSerializer