from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializer import *


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
