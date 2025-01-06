from rest_framework import permissions
from .models import Student, Teacher

class IsStudentOrTeacherOfStudent(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только самому ученику или его учителю.
    """

    def has_permission(self, request, view):

        # Получаем ID студента из URL
        student_id = view.kwargs.get('student_id')

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return False

        # Если пользователь - ученик, проверяем, что это его профиль
        if request.user.role == 'ученик':
            return student.account.id == request.user.id

        # Если пользователь - учитель, проверяем, что студент есть в его списке студентов
        if request.user.role == 'учитель':
            try:
                teacher = Teacher.objects.get(account=request.user)
                return student in teacher.students.all()
            except Teacher.DoesNotExist:
                return False

        # Во всех остальных случаях доступ запрещен
        return False