from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializer import *


class GetUpcomingLessonsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получаем текущего пользователя
        user = request.user

        # Создаем словарь для хранения ближайших занятий
        upcoming_lessons = {}

        if user.role == 'ученик':
            try:
                # Получаем профиль ученика
                student = Student.objects.get(account=user)
            except Student.DoesNotExist:
                return Response({"error": "Профиль ученика не найден"}, status=status.HTTP_404_NOT_FOUND)

            # Получаем всех учителей, связанных с учеником
            teachers = student.teacher_students.all()

            # Для каждого учителя находим ближайшее занятие
            for teacher in teachers:
                # Получаем все занятия с этим учителем, которые еще не прошли
                lessons = Lesson.objects.filter(
                    teacher=teacher,
                    student=student,
                    datetime__gte=datetime.now()  # Используем datetime.now()
                ).order_by('datetime')  # Сортируем по дате и времени

                if lessons.exists():
                    # Берем ближайшее занятие
                    nearest_lesson = lessons.first()

                    # Форматируем дату и время
                    formatted_datetime = nearest_lesson.datetime.strftime('%H:%M %d.%m.%Y')
                    upcoming_lessons[teacher.account.username] = formatted_datetime
                else:
                    # Если занятий нет, добавляем пустую строку
                    upcoming_lessons[teacher.account.username] = ""

        elif user.role == 'учитель':
            try:
                # Получаем профиль учителя
                teacher = Teacher.objects.get(account=user)
            except Teacher.DoesNotExist:
                return Response({"error": "Профиль учителя не найден"}, status=status.HTTP_404_NOT_FOUND)

            # Получаем всех учеников, связанных с учителем
            students = teacher.students.all()

            # Для каждого ученика находим ближайшее занятие
            for student in students:
                # Получаем все занятия с этим учеником, которые еще не прошли
                lessons = Lesson.objects.filter(
                    teacher=teacher,
                    student=student,
                    datetime__gte=datetime.now()  # Используем datetime.now()
                ).order_by('datetime')  # Сортируем по дате и времени

                if lessons.exists():
                    # Берем ближайшее занятие
                    nearest_lesson = lessons.first()

                    # Форматируем дату и время
                    formatted_datetime = nearest_lesson.datetime.strftime('%H:%M %d.%m.%Y')
                    upcoming_lessons[student.account.username] = formatted_datetime
                else:
                    # Если занятий нет, добавляем пустую строку
                    upcoming_lessons[student.account.username] = ""

        else:
            return Response({"error": "Доступ разрешен только для учеников и учителей"},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(upcoming_lessons, status=status.HTTP_200_OK)
