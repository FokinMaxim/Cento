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

class IsTeacher(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только пользователям с ролью 'учитель'.
    """

    def has_permission(self, request, view):
        return request.user.role == 'учитель'


class IsStudent(permissions.BasePermission):
    """
    Разрешение, которое позволяет доступ только пользователям с ролью 'учитель'.
    """

    def has_permission(self, request, view):
        return request.user.role == 'ученик'


class IsAssignedTo(permissions.BasePermission):
    """
    Разрешение для ученика или его учителя, приписанных к объекту
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ученик':
            return obj.student.account == request.user
        elif request.user.role == 'учитель':
            return obj.teacher == request.user.teacher
        return False