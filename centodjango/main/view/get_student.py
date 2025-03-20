from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..permissions import IsStudentOrTeacherOfStudent
from ..models import *
from ..serializer import *


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentOrTeacherOfStudent])
def getStudent(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

    # Сериализация данных об ученике
    student_serializer = StudentSerializer(student)

    # Получение вариантов, которые заданы ученику
    assigned_variants = TeachersVariantStudent.objects.filter(fk_student_id=student)
    variants_data = []
    for variant in assigned_variants:
        variants_data.append({
            "variant_id": variant.fk_variant_id.id,  # Используем id вместо variant_id
            "dead_line": variant.dead_line,
            "teacher": variant.fk_teacher_id.account.username
        })

    # Получение учителей, к которым привязан ученик
    teachers = student.teacher_students.all()
    teachers_data = [{"teacher_id": teacher.account.id, "teacher_name": teacher.account.username} for teacher in
                     teachers]

    # Формирование ответа
    response_data = {
        "student": student_serializer.data,
        "assigned_variants": variants_data,
        "teachers": teachers_data
    }

    return Response(response_data, status=status.HTTP_200_OK)
