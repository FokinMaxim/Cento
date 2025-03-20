from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializer import *
from ..permissions import IsTeacher

@permission_classes([IsAuthenticated, IsTeacher])
class AddStudentToTeacherView(APIView):
    def post(self, request):
        # Получаем почту ученика из запроса
        student_email = request.data.get('student_email')
        if not student_email:
            return Response({"error": "Student email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Находим аккаунт ученика по почте
            student_account = Account.objects.get(email=student_email, role='ученик')
        except Account.DoesNotExist:
            return Response({"error": "Student with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Находим профиль ученика
            student = Student.objects.get(account=student_account)
        except Student.DoesNotExist:
            return Response({"error": "Student profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        # Находим учителя, который отправил запрос
        teacher = Teacher.objects.get(account=request.user)
        # Добавляем ученика в список студентов учителя
        teacher.students.add(student)
        return Response({"message": "Student added successfully"}, status=status.HTTP_200_OK)

