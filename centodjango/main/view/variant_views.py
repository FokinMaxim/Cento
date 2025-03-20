from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..permissions import IsTeacher
from ..models import *
from ..serializer import *


@permission_classes([IsAuthenticated])
class CombinedVariantsView(APIView):
    def get(self, request):
        user = request.user
        variants = Variant.objects.filter(visibility=True)
        # Если пользователь - учитель, добавляем его варианты
        if user.role == 'учитель':
            try:
                teacher = Teacher.objects.get(account=user)
                teacher_variants = Variant.objects.filter(creator_id=teacher)
                variants = variants | teacher_variants
            except Teacher.DoesNotExist:
                pass  # Если пользователь не является учителем, просто пропускаем

        # Сериализуем все варианты и возвращаем их
        serializer = VariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def create_variant(request):
    data = request.data

    # Получаем объект учителя, который создает вариант
    teacher = get_object_or_404(Teacher, account=request.user)

    # Проверяем, что переданные ID экзамена и заданий существуют
    exam_id = data.get('fk_exam_id')
    task_ids = data.get('tasks', [])

    if not exam_id or not task_ids:
        return Response({"error": "Exam ID and task IDs are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем объект экзамена
    exam = get_object_or_404(Exam, id=exam_id)

    # Получаем все задачи по переданным ID
    tasks = Task.objects.filter(id__in=task_ids)

    for task in tasks:
        if task.creator_id and task.creator_id != teacher:
            return Response(
                {
                    "error": f"Task {task.id} was created by another teacher. "
                             "You can only use your own tasks or public tasks."
                },
                status=status.HTTP_403_FORBIDDEN
            )

    # Создаем вариант
    variant = Variant.objects.create(
        creator_id=teacher,
        visibility=data.get('visibility', True),
        time_limit=data.get('time_limit', None),
        fk_exam_id=exam
    )

    # Добавляем задачи в вариант
    variant.tasks.set(tasks)

    # Сериализуем и возвращаем созданный вариант
    serializer = VariantSerializer(variant)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_all_variants(request):
    try:
        # Получаем все объекты Variant из базы данных
        variants = Variant.objects.all()

        # Создаем список для хранения данных о вариантах
        variants_data = []

        for variant in variants:
            # Сериализуем вариант
            variant_serializer = VariantSerializer(variant)
            variant_data = variant_serializer.data

            # Получаем все задачи, связанные с этим вариантом
            tasks = variant.tasks.all()

            # Сериализуем задачи
            task_serializer = TaskSerializer(tasks, many=True)

            # Добавляем полную информацию о задачах в данные варианта
            variant_data['tasks'] = task_serializer.data

            # Добавляем вариант в список
            variants_data.append(variant_data)

        # Возвращаем данные в ответе
        return Response(variants_data, status=status.HTTP_200_OK)

    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_variant_by_id(request, variant_id):
    try:
        # Получаем объект Variant по ID
        variant = get_object_or_404(Variant, id=variant_id)

        # Сериализуем вариант
        variant_serializer = VariantSerializer(variant)
        variant_data = variant_serializer.data

        # Получаем все задачи, связанные с этим вариантом
        tasks = variant.tasks.all()

        # Сериализуем задачи
        task_serializer = TaskSerializer(tasks, many=True)

        # Добавляем полную информацию о задачах в данные варианта
        variant_data['tasks'] = task_serializer.data

        # Возвращаем данные в ответе
        return Response(variant_data, status=status.HTTP_200_OK)

    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)