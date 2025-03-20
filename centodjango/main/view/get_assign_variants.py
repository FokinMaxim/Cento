from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..permissions import IsTeacher
from ..models import *
from ..serializer import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_variants(request):
    """
    Возвращает список объектов из модели TeachersVariantStudent, связанных с учеником.
    Учеником является пользователь, отправивший запрос.
    """
    try:
        # Проверяем, что пользователь является учеником
        if request.user.role != 'ученик':
            return Response({"error": "Доступ разрешен только для учеников"}, status=status.HTTP_403_FORBIDDEN)

        # Получаем профиль ученика
        student = Student.objects.get(account=request.user)

        # Получаем все объекты TeachersVariantStudent, связанные с этим учеником
        assigned_variants = TeachersVariantStudent.objects.filter(fk_student_id=student)

        # Сериализуем данные
        serializer = TeachersVariantStudentSerializer(assigned_variants, many=True)

        # Возвращаем сериализованные данные
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        # Если профиль ученика не найден
        return Response({"error": "Профиль ученика не найден"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)