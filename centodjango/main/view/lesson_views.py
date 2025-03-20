from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializer import *


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'учитель':
            # Возвращаем все уроки, где учитель — это текущий пользователь
            return Lesson.objects.filter(teacher__account=user)
        elif user.role == 'ученик':
            # Возвращаем все уроки, где ученик — это текущий пользователь
            return Lesson.objects.filter(student__account=user)
        else:
            return Lesson.objects.none()

    def post(self, request, *args, **kwargs):
        """
        Обработка POST-запроса для создания урока.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Валидация данных
        serializer.save()  # Создание урока
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LessonDeleteView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Проверяем, что запрос отправляет учитель
        if request.user.role != 'учитель':
            return Response({"detail": "Только учитель может удалять уроки."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
