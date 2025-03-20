from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..permissions import IsTeacher
from ..models import *
from ..serializer import *


class CreateHomeworkView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        # Получаем данные из запроса
        variant_id = request.data.get('variant_id')
        student_email = request.data.get('student_email')
        dead_line = request.data.get('dead_line')

        # Проверяем, что все необходимые данные переданы
        if not variant_id or not student_email or not dead_line:
            return Response(
                {"error": "Variant ID, student email, and deadline are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект варианта
        variant = get_object_or_404(Variant, id=variant_id)

        # Получаем объект учителя, который отправил запрос
        teacher = get_object_or_404(Teacher, account=request.user)

        # Проверяем, что вариант либо создан текущим учителем, либо является общим (creator == null)
        if variant.creator_id and variant.creator_id != teacher:
            return Response(
                {"error": "You can only assign your own variants or public variants"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем объект ученика по почте
        try:
            student_account = Account.objects.get(email=student_email, role='ученик')
            student = Student.objects.get(account=student_account)
        except Account.DoesNotExist:
            return Response(
                {"error": "Student with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Student.DoesNotExist:
            return Response(
                {"error": "Student profile does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, что ученик привязан к учителю
        if student not in teacher.students.all():
            return Response(
                {"error": "This student is not assigned to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Создаем объект TeachersVariantStudent
        teachers_variant_student = TeachersVariantStudent.objects.create(
            fk_teacher_id=teacher,
            fk_student_id=student,
            fk_variant_id=variant,
            dead_line=dead_line,
            status='задано'  # Устанавливаем статус по умолчанию
        )

        # Сериализуем и возвращаем созданный объект
        serializer = TeachersVariantStudentSerializer(teachers_variant_student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
