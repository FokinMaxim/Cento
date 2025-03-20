from rest_framework import viewsets
from ..models import *
from ..serializer import *


class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TypeOfTaskViewSet(viewsets.ModelViewSet):
    queryset = TypeOfTask.objects.all()
    serializer_class = TypeOfTaskSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class TeachersVariantStudentViewSet(viewsets.ModelViewSet):
    queryset = TeachersVariantStudent.objects.all()
    serializer_class = TeachersVariantStudentSerializer
