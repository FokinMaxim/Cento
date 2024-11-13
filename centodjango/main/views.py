from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework.views import APIView
from  .models import Student
from .serializer import StudentSerializer
from rest_framework.response import Response

class StudentView(APIView):
    def get(self, request):
        output = Student.objects.all().values()
        return Response({'posts': list(output)})

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)