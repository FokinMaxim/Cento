from datetime import timedelta
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
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
            # хэшируем пароль
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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_data = {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
        }

        if user.role == 'ученик':
            try:
                student = Student.objects.get(account=user)
                profile_data["student"] = StudentSerializer(student).data

                # Получаем список учителей, связанных с этим учеником
                teachers = student.teacher_students.all()
                teachers_data = [{
                    "teacher_id": teacher.account.id,
                    "teacher_name": teacher.account.username,
                    "teacher_email": teacher.account.email
                } for teacher in teachers]

                profile_data["teachers"] = teachers_data

            except Student.DoesNotExist:
                profile_data["student"] = None
                profile_data["teachers"] = []

        elif user.role == 'учитель':
            try:
                teacher = Teacher.objects.get(account=user)
                profile_data["teacher"] = TeacherSerializer(teacher).data

                # Получаем список учеников, связанных с этим учителем
                students = teacher.students.all()
                students_data = [{
                    "student_id": student.account.id,
                    "student_name": student.account.username,
                    "student_email": student.account.email
                } for student in students]

                profile_data["students"] = students_data

            except Teacher.DoesNotExist:
                profile_data["teacher"] = None
                profile_data["students"] = []

        return Response(profile_data, status=status.HTTP_200_OK)


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


class CreateHomeworkView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        # Получаем данные из запроса
        variant_id = request.data.get('variant_id')
        student_email = request.data.get('student_email')
        dead_line = request.data.get('dead_line')

        # Проверяем, что все необходимые данные переданы
        if not variant_id or not student_email or not dead_line:
            return Response(
                {"error": "Variant ID, student email, and deadline are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект варианта
        variant = get_object_or_404(Variant, id=variant_id)

        # Получаем объект учителя, который отправил запрос
        teacher = get_object_or_404(Teacher, account=request.user)

        # Проверяем, что вариант либо создан текущим учителем, либо является общим (creator == null)
        if variant.creator_id and variant.creator_id != teacher:
            return Response(
                {"error": "You can only assign your own variants or public variants"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем объект ученика по почте
        try:
            student_account = Account.objects.get(email=student_email, role='ученик')
            student = Student.objects.get(account=student_account)
        except Account.DoesNotExist:
            return Response(
                {"error": "Student with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Student.DoesNotExist:
            return Response(
                {"error": "Student profile does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, что ученик привязан к учителю
        if student not in teacher.students.all():
            return Response(
                {"error": "This student is not assigned to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Создаем объект TeachersVariantStudent
        teachers_variant_student = TeachersVariantStudent.objects.create(
            fk_teacher_id=teacher,
            fk_student_id=student,
            fk_variant_id=variant,
            dead_line=dead_line,
            status='задано'  # Устанавливаем статус по умолчанию
        )

        # Сериализуем и возвращаем созданный объект
        serializer = TeachersVariantStudentSerializer(teachers_variant_student)
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


class CheckVariantView(APIView):
    permission_classes = [IsAuthenticated]  # Только для аутентифицированных пользователей

    def post(self, request):
        # Проверяем, что запрос отправляет ученик
        if request.user.role != 'ученик':
            return Response(
                {"error": "Only students can submit answers"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем данные из запроса
        variant_id = request.data.get('variant_id')
        student_answers = request.data.get('answers')  # Словарь с ответами ученика

        # Проверяем, что все необходимые данные переданы
        if not variant_id or not student_answers:
            return Response(
                {"error": "Variant ID and answers are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект варианта
        variant = get_object_or_404(Variant, id=variant_id)

        # Получаем все задачи, связанные с этим вариантом
        tasks = variant.tasks.all()

        # Инициализируем переменные для подсчёта баллов
        total_points = 0

        # Проверяем ответы ученика
        for task in tasks:
            if str(task.id) in student_answers:  # Проверяем, есть ли ответ на это задание
                student_answer = student_answers[str(task.id)]
                if student_answer == task.correct_answer:  # Сравниваем ответ ученика с правильным
                    total_points += task.fk_code_of_type.points  # Добавляем баллы за задание

        # Получаем объект TeachersVariantStudent для обновления
        try:
            teachers_variant_student = TeachersVariantStudent.objects.get(
                fk_variant_id=variant,
                fk_student_id__account=request.user  # Ученик, который отправил запрос
            )
        except TeachersVariantStudent.DoesNotExist:
            return Response(
                {"error": "This variant is not assigned to you"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Обновляем earned_points и статус
        teachers_variant_student.earned_points = total_points
        teachers_variant_student.status = 'решено'  # Меняем статус на "проверено"
        teachers_variant_student.save()

        # Возвращаем результат
        return Response(
            {
                "message": "Variant checked successfully"
            },
            status=status.HTTP_200_OK
        )


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Проверяем, что запрос отправляет учитель
        if request.user.role != 'учитель':
            return Response({"detail": "Только учитель может удалять уроки."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


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