from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time
from ..models import ScheduleElement
from ..serializer import ScheduleElementSerializer
from ..permissions import IsTeacher, IsAssignedTo, IsStudent


class TeacherSchedulePeriodView(generics.ListAPIView):
    serializer_class = ScheduleElementSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        start_date = self.request.data.get('start_date')
        end_date = self.request.data.get('end_date')
        print(start_date, end_date)

        # Преобразуем строки в datetime
        try:
            start_datetime = datetime.combine(
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                time.min
            )
            end_datetime = datetime.combine(
                datetime.strptime(end_date, '%Y-%m-%d').date(),
                time.max
            )
        except (ValueError, TypeError):
            raise TypeError({'message': 'Неправильный формат даты'})

        # Получаем занятия учителя в указанном периоде
        return ScheduleElement.objects.filter(
            teacher=self.request.user.teacher,
            datetime__gte=start_datetime,
            datetime__lte=end_datetime
        ).order_by('datetime')


class StudentSchedulePeriodView(generics.ListAPIView):
    serializer_class = ScheduleElementSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        start_date = self.request.data.get('start_date')
        end_date = self.request.data.get('end_date')

        # Преобразуем строки в datetime
        try:
            start_datetime = datetime.combine(
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                time.min)
            end_datetime = datetime.combine(
                datetime.strptime(end_date, '%Y-%m-%d').date(),
                time.max)
        except (ValueError, TypeError):
            return ScheduleElement.objects.none()

        # Получаем занятия ученика в указанном периоде
        return ScheduleElement.objects.filter(
            student=self.request.user.student,
            datetime__gte=start_datetime,
            datetime__lte=end_datetime
        ).order_by('datetime')