from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializer import *

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_data = {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
        }

        if user.role == 'ученик':
            try:
                student = Student.objects.get(account=user)
                profile_data["student"] = StudentSerializer(student).data

                # Получаем список учителей, связанных с этим учеником
                teachers = student.teacher_students.all()
                teachers_data = [{
                    "teacher_id": teacher.account.id,
                    "teacher_name": teacher.account.username,
                    "teacher_email": teacher.account.email
                } for teacher in teachers]

                profile_data["teachers"] = teachers_data

            except Student.DoesNotExist:
                profile_data["student"] = None
                profile_data["teachers"] = []

        elif user.role == 'учитель':
            try:
                teacher = Teacher.objects.get(account=user)
                profile_data["teacher"] = TeacherSerializer(teacher).data

                # Получаем список учеников, связанных с этим учителем
                students = teacher.students.all()
                students_data = [{
                    "student_id": student.id,
                    "student_name": student.account.username,
                    "student_email": student.account.email
                } for student in students]

                profile_data["students"] = students_data

            except Teacher.DoesNotExist:
                profile_data["teacher"] = None
                profile_data["students"] = []

        return Response(profile_data, status=status.HTTP_200_OK)
