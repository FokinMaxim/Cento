from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializer import *


class CheckVariantView(APIView):
    permission_classes = [IsAuthenticated]  # Только для аутентифицированных пользователей

    def post(self, request):
        # Проверяем, что запрос отправляет ученик
        if request.user.role != 'ученик':
            return Response(
                {"error": "Only students can submit answers"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем данные из запроса
        variant_id = request.data.get('variant_id')
        student_answers = request.data.get('answers')  # Словарь с ответами ученика

        # Проверяем, что все необходимые данные переданы
        if not variant_id or not student_answers:
            return Response(
                {"error": "Variant ID and answers are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект варианта
        variant = get_object_or_404(Variant, id=variant_id)

        # Получаем все задачи, связанные с этим вариантом
        tasks = variant.tasks.all()

        # Инициализируем переменные для подсчёта баллов
        total_points = 0

        # Проверяем ответы ученика
        for task in tasks:
            if str(task.id) in student_answers:  # Проверяем, есть ли ответ на это задание
                student_answer = student_answers[str(task.id)]
                if student_answer == task.correct_answer:  # Сравниваем ответ ученика с правильным
                    total_points += task.fk_code_of_type.points  # Добавляем баллы за задание

        # Получаем объект TeachersVariantStudent для обновления
        try:
            teachers_variant_student = TeachersVariantStudent.objects.get(
                fk_variant_id=variant,
                fk_student_id__account=request.user  # Ученик, который отправил запрос
            )
        except TeachersVariantStudent.DoesNotExist:
            return Response(
                {"error": "This variant is not assigned to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Обновляем earned_points и статус
        teachers_variant_student.earned_points = total_points
        teachers_variant_student.status = 'решено'  # Меняем статус на "проверено"
        teachers_variant_student.save()

        # Возвращаем результат
        return Response(
            {
                "message": "Variant checked successfully"
            },
            status=status.HTTP_200_OK
        )