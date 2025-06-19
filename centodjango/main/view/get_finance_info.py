from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.db.models import Sum
from collections import defaultdict
import calendar
from rest_framework import generics, request
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, date
from ..models import ScheduleElement
from ..serializer import ScheduleElementSerializer
from ..permissions import IsTeacher


class LessonsPaidStatusView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        try:
            payment_status = request.data.get('payment_status')
            if payment_status not in ['paid', 'not_paid']:
                raise ValidationError("Недопустимый статус оплаты. Используйте 'paid' или 'not_paid'")

            # Добавляем параметры периода
            start_date_str = request.data['start_date']
            end_date_str = request.data['end_date']

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        except KeyError as e:
            if str(e) == "'payment_status'":
                raise ValidationError("Не указан обязательный параметр 'payment_status'")
            else:
                raise ValidationError("Не указаны обязательные параметры 'start_date' и 'end_date'")
        except ValueError:
            raise ValidationError("Неверный формат даты. Используйте YYYY-MM-DD")

        teacher = request.user.teacher

        lessons = ScheduleElement.objects.filter(
            teacher=teacher,
            datetime__date__gte=start_date,
            datetime__date__lte=end_date,
            payment_status=payment_status,
        ).order_by('-datetime')

        serializer = ScheduleElementSerializer(lessons, many=True)
        return Response(serializer.data)


class TeacherFinancialStatsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        try:
            input_data = request.data
            start_date_str = input_data['start_date']
            end_date_str = input_data['end_date']
            exams = input_data.get('exams', [])  # список exam_name (опционально)

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except KeyError:
            return Response({'error': 'Не указаны обязательные параметры start_date и end_date'}, status=400)
        except ValueError:
            return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)

        # Получаем учителя из токена
        teacher = request.user.teacher

        # Базовый запрос
        queryset = ScheduleElement.objects.filter(
            teacher=teacher,
            datetime__date__gte=start_date,
            datetime__date__lte=end_date,
            payment_status='paid'
        )

        # Фильтрация по предметам если они указаны
        if exams:
            queryset = queryset.filter(exam__exam_name__in=exams)

        # Группируем данные
        stats = queryset.values(
            'datetime__year',
            'datetime__month',
            'exam__exam_name'
        ).annotate(
            total_amount=Sum('lesson_cost')
        ).order_by('datetime__year', 'datetime__month')

        # Создаем структуру для результата
        result = defaultdict(lambda: defaultdict(dict))

        # Месяца на русском
        month_names = {
            1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
            5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
            9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
        }

        for item in stats:
            year = str(item['datetime__year'])
            month = month_names[item['datetime__month']]
            exam = item['exam__exam_name']
            amount = float(item['total_amount'])

            result[year][month][exam] = amount

        # Добавляем все месяцы в период, даже если нет данных
        current_date = start_date
        while current_date <= end_date:
            year = str(current_date.year)
            month = month_names[current_date.month]

            if month not in result[year]:
                result[year][month] = {}

            # Переходим к следующему месяцу
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)

        return Response(result)