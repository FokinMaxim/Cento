from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..permissions import IsTeacher
from ..models import *
from ..serializer import *


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def create_task(request):
    data = request.data
    # Получаем объект учителя, который создает задание
    teacher = get_object_or_404(Teacher, account=request.user)
    # Проверяем, что переданные ID типа задания и экзамена существуют
    type_of_task_id = data.get('fk_code_of_type')
    exam_id = data.get('fk_exam_id')

    if not type_of_task_id or not exam_id:
        return Response({"error": "Type of task and exam IDs are required"}, status=status.HTTP_400_BAD_REQUEST)

    type_of_task = get_object_or_404(TypeOfTask, id=type_of_task_id)
    exam = get_object_or_404(Exam, id=exam_id)

    # Создаем задание
    task = Task.objects.create(
        fk_code_of_type=type_of_task,
        creator_id=teacher,
        visibility=data.get('visibility', True),
        fk_exam_id=exam,
        description=data.get('description', ''),
        image_path=data.get('image_path', ''),
        correct_answer=data.get('correct_answer', ''),
        file_path=data.get('file_path', '')
    )
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
class CombinedTasksView(APIView):
    def get(self, request):
        user = request.user
        tasks = Task.objects.filter(visibility=True)
        # Если пользователь - учитель, добавляем его задания
        if user.role == 'учитель':
            try:
                teacher = Teacher.objects.get(account=user)
                teacher_tasks = Task.objects.filter(creator_id=teacher)
                tasks = tasks | teacher_tasks
            except Teacher.DoesNotExist:
                pass  # Если пользователь не является учителем, просто пропускаем

        # Сериализуем все задачи и возвращаем их
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
