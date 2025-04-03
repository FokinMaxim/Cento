from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsTeacher
from ..serializer import StudentSerializer
from ..models import Teacher, Student

class TeacherStudentsListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        # Получаем объект учителя для текущего пользователя
        teacher = self.request.user.teacher
        # Возвращаем всех студентов, привязанных к этому учителю
        return teacher.students.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Добавляем дополнительную информацию в ответ
        response.data = {
            'teacher': request.user.username,
            'students_count': len(response.data),
            'students': response.data
        }
        return response