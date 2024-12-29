from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from  .models import *
from .serializer import *
from rest_framework import viewsets, permissions, generics, status


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

@api_view(['GET'])
def getStudent(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

    # Сериализация данных об ученике
    student_serializer = StudentSerializer(student)

    # Получение вариантов, которые заданы ученику
    assigned_variants = TeachersVariantStudent.objects.filter(fk_student_id=student)
    variants_data = []
    for variant in assigned_variants:
        variants_data.append({
            "variant_id": variant.fk_variant_id.variant_id,
            "dead_line": variant.dead_line,
            "teacher": variant.fk_teacher_id.account.username
        })

    # Получение учителей, к которым привязан ученик
    teachers = student.teacher_students.all()
    teachers_data = [{"teacher_id": teacher.account.id, "teacher_name": teacher.account.username} for teacher in teachers]

    # Формирование ответа
    response_data = {
        "student": student_serializer.data,
        "assigned_variants": variants_data,
        "teachers": teachers_data
    }

    return Response(response_data, status=status.HTTP_200_OK)