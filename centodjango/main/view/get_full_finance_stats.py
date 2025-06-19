from collections import defaultdict
from datetime import date, datetime

from django.db.models import Count, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ScheduleElement
from ..permissions import IsTeacher


class TeacherCombinedFinancialStatsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        try:
            input_data = request.data
            start_date_str = input_data['start_date']
            end_date_str = input_data['end_date']
            exams = input_data.get('exams', [])

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except KeyError:
            return Response({'error': 'Не указаны обязательные параметры start_date и end_date'}, status=400)
        except ValueError:
            return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)

        teacher = request.user.teacher
        base_queryset = self.get_base_queryset(teacher, start_date, end_date, exams)

        # Получаем все статистики
        earned_money, total_earned_money = self.get_financial_stats(base_queryset.filter(payment_status='paid'),
                                                                    start_date, end_date)
        potential_money, total_potential_money = self.get_financial_stats(base_queryset, start_date, end_date)
        earned_lessons, total_earned_lessons = self.get_lessons_stats(base_queryset.filter(payment_status='paid'),
                                                                      start_date, end_date)
        potential_lessons, total_potential_lessons = self.get_lessons_stats(base_queryset, start_date, end_date)
        total_paid_hours = self.get_total_paid_hours(base_queryset.filter(payment_status='paid'))

        earnings_per_hour = 0
        if total_paid_hours > 0 and total_earned_money is not None:
            earnings_per_hour = round(total_earned_money / total_paid_hours, 2)

        return Response({
            'earned_money': {
                'detailed_stat': earned_money,
                'total_sum': total_earned_money
            },
            'potential_money': {
                'detailed_stat': potential_money,
                'total_sum': total_potential_money
            },
            'earned_lessons': {
                'detailed_stat': earned_lessons,
                'total_sum': total_earned_lessons
            },
            'potential_lessons': {
                'detailed_stat': potential_lessons,
                'total_sum': total_potential_lessons
            },
            'total_paid_hours': total_paid_hours,
            'earnings_per_hour': earnings_per_hour
        })

    def get_total_paid_hours(self, queryset):
        """Вычисляет общее количество часов оплаченных занятий"""
        total_minutes = queryset.aggregate(
            total_minutes=Sum('duration')
        )['total_minutes'] or 0

        # Конвертируем минуты в часы с округлением до 2 знаков
        total_hours = round(total_minutes / 60, 2)
        return total_hours

    # Остальные методы остаются без изменений
    def get_base_queryset(self, teacher, start_date, end_date, exams):
        """Базовый запрос с общими фильтрами"""
        queryset = ScheduleElement.objects.filter(
            teacher=teacher,
            datetime__date__gte=start_date,
            datetime__date__lte=end_date
        )
        if exams:
            queryset = queryset.filter(exam__exam_name__in=exams)
        return queryset

    def get_monthly_structure(self, start_date, end_date):
        """Создает структуру для хранения данных по месяцам"""
        result = defaultdict(lambda: defaultdict(dict))
        month_names = {
            1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
            5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
            9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
        }

        current_date = start_date
        while current_date <= end_date:
            year = str(current_date.year)
            month = month_names[current_date.month]
            result[year][month]  # Инициализируем месяц

            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)

        return result, month_names

    def get_financial_stats(self, queryset, start_date, end_date):
        """Статистика по денежным суммам с общей суммой"""
        stats = queryset.values(
            'datetime__year',
            'datetime__month',
            'exam__exam_name'
        ).annotate(
            total_amount=Sum('lesson_cost')
        ).order_by('datetime__year', 'datetime__month')

        result, month_names = self.get_monthly_structure(start_date, end_date)
        total_sum = 0

        for item in stats:
            year = str(item['datetime__year'])
            month = month_names[item['datetime__month']]
            exam = item['exam__exam_name']
            amount = float(item['total_amount'])
            result[year][month][exam] = amount
            total_sum += amount

        return result, total_sum

    def get_lessons_stats(self, queryset, start_date, end_date):
        """Статистика по количеству занятий с общим количеством"""
        stats = queryset.values(
            'datetime__year',
            'datetime__month',
            'exam__exam_name'
        ).annotate(
            lessons_count=Count('id')
        ).order_by('datetime__year', 'datetime__month')

        result, month_names = self.get_monthly_structure(start_date, end_date)
        total_count = 0

        for item in stats:
            year = str(item['datetime__year'])
            month = month_names[item['datetime__month']]
            exam = item['exam__exam_name']
            count = item['lessons_count']
            result[year][month][exam] = count
            total_count += count

        return result, total_count