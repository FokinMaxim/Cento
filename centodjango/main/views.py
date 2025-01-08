from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .permissions import *
from .serializer import *
from rest_framework import viewsets, generics, status



class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer


class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TypeOfTaskViewSet(viewsets.ModelViewSet):
    queryset = TypeOfTask.objects.all()
    serializer_class = TypeOfTaskSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class TeachersVariantStudentViewSet(viewsets.ModelViewSet):
    queryset = TeachersVariantStudent.objects.all()
    serializer_class = TeachersVariantStudentSerializer


class RegisterView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = RegisterSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


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


class RegisterStudentView(APIView):
    def post(self, request):
        serializer = RoleBasedRegisterSerializer(data=request.data)
        if serializer.is_valid():
            #хэшируем пароль
            password = make_password(serializer.validated_data['password'])
            # Создаем аккаунт
            account = Account.objects.create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=password,
                phone_number=serializer.validated_data.get('phone_number', ''),
                role='ученик'  # Устанавливаем роль ученика
            )
            # Создаем профиль ученика
            studying_year = request.data.get('studying_year')
            Student.objects.create(account=account, studying_year=studying_year)

            return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterTeacherView(APIView):
    def post(self, request):
        serializer = RoleBasedRegisterSerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data['password'])
            # Создаем аккаунт
            account = Account.objects.create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=password,
                phone_number=serializer.validated_data.get('phone_number', ''),
                role='учитель'  # Устанавливаем роль учителя
            )
            # Получаем данные для модели Teacher
            tariff_id = request.data.get('tariff_id')  # Получаем ID тарифа из запроса
            tariff = Tariff.objects.get(id=tariff_id)  # Находим объект Tariff по id

            # Вычисляем дату окончания тарифа (текущая дата + 6 месяцев)
            tariff_end_date = datetime.now() + timedelta(days=180)  # 180 дней = ~6 месяцев

            # Создаем профиль учителя
            teacher = Teacher.objects.create(
                account=account,
                fk_tariff_id=tariff,
                tariff_end_date=tariff_end_date
            )
            # Добавляем экзамены, если они переданы в запросе
            exam_ids = request.data.get('exams', [])  # Получаем список ID экзаменов
            if exam_ids:
                exams = Exam.objects.filter(id__in=exam_ids)  # Находим объекты Exam по ID
                teacher.exams.set(exams)  # Устанавливаем экзамены для учителя
            return Response({"message": "Teacher registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated, IsTeacher])
class AddStudentToTeacherView(APIView):
    def post(self, request):
        # Получаем почту ученика из запроса
        student_email = request.data.get('student_email')
        if not student_email:
            return Response({"error": "Student email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Находим аккаунт ученика по почте
            student_account = Account.objects.get(email=student_email, role='ученик')
        except Account.DoesNotExist:
            return Response({"error": "Student with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Находим профиль ученика
            student = Student.objects.get(account=student_account)
        except Student.DoesNotExist:
            return Response({"error": "Student profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        # Находим учителя, который отправил запрос
        teacher = Teacher.objects.get(account=request.user)
        # Добавляем ученика в список студентов учителя
        teacher.students.add(student)
        return Response({"message": "Student added successfully"}, status=status.HTTP_200_OK)


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