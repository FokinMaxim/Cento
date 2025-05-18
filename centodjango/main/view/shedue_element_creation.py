from django.db.models import F, ExpressionWrapper, DurationField
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import timedelta
from ..models import ScheduleElement, RecurringScheduleElement, Student, Exam
from ..serializer import ScheduleElementCreateSerializer
from ..permissions import IsTeacher


class ScheduleElementCreateView(generics.CreateAPIView):
    serializer_class = ScheduleElementCreateSerializer
    permission_classes = [IsTeacher]

    def perform_create(self, serializer):
        data = serializer.validated_data
        teacher = self.request.user.teacher

        # Проверка, что ученик принадлежит учителю
        student = self.get_student(data['student_id'], teacher)

        # Проверка экзамена (если указан)
        exam = self.validate_exam(data.get('exam_id'), student)

        # Проверка на конфликты расписания
        self.check_schedule_conflicts(
            teacher=teacher,
            start_time=data['datetime'],
            duration=data['duration']
        )

        # Создаем занятие
        if data['is_repetitive']:
            schedule_element = self.create_recurring_schedule(
                teacher=teacher,
                student=student,
                exam=exam,
                data=data
            )
        else:
            schedule_element = ScheduleElement.objects.create(
                teacher=teacher,
                student=student,
                exam=exam,
                **{k: v for k, v in data.items() if k not in ['student_id', 'exam_id', 'is_repetitive']}
            )

        serializer.instance = schedule_element

    def get_student(self, student_id, teacher):
        try:
            student = Student.objects.get(id=student_id)
            if not teacher.students.filter(id=student.id).exists():
                raise ValidationError("Этот ученик не привязан к вам")
            return student
        except Student.DoesNotExist:
            raise ValidationError("Ученик не найден")

    def validate_exam(self, exam_id, student):
        if exam_id:
            try:
                exam = Exam.objects.get(id=exam_id)
                if not student.exams.filter(id=exam.id).exists():
                    raise ValidationError(f"Ученик не готовится к указанному экзамену")
                return exam
            except Exam.DoesNotExist:
                raise ValidationError("Экзамен не найден")
        return None

    def check_schedule_conflicts(self, teacher, start_time, duration):
        """
        Проверяет пересечение нового занятия с существующими.
        teacher: объект Teacher
        start_time: datetime начала нового занятия
        duration: длительность нового занятия в минутах
        """
        # Временные границы нового занятия
        new_start = start_time
        new_end = new_start + timedelta(minutes=duration)

        # Находим все занятия учителя, которые могут пересекаться с новым
        conflicting_lessons = ScheduleElement.objects.filter(
            teacher=teacher,
            datetime__lt=new_end,  # Существующее занятие начинается ДО конца нового
            datetime__gte=new_start - timedelta(minutes=1440)  # За последние 24 часа (оптимизация)
        ).annotate(
            end_time=ExpressionWrapper(
                F('datetime') + ExpressionWrapper(
                    F('duration') * timedelta(minutes=1),
                    output_field=DurationField()
                ),
                output_field=DurationField()
            )
        ).filter(
            end_time__gt=new_start  # Существующее занятие заканчивается ПОСЛЕ начала нового
        )

        if conflicting_lessons.exists():
            conflicts = []
            for lesson in conflicting_lessons:
                conflicts.append({
                    'id': lesson.id,
                    'start': lesson.datetime,
                    'end': lesson.datetime + timedelta(minutes=lesson.duration),
                    'name': lesson.lesson_name
                })
            raise ValidationError({
                'message': 'Обнаружено пересечение с существующими занятиями',
                'conflicts': conflicts
            })

    def create_recurring_schedule(self, teacher, student, exam, data):
        """Создает шаблон повторяющегося занятия и первые 3 занятия"""
        # Создаем шаблон
        #recurring_element = RecurringScheduleElement.objects.create(
        #    teacher=teacher,
        #    student=student,
        #    exam=exam,
        #    lesson_name=data['lesson_name'],
        #    day_of_week=data['datetime'].weekday(),
        #    time=data['datetime'].time(),
        #    duration=data['duration'],
        #    color=data.get('color', '#3b82f6')
        #)

        # Создаем первые 3 занятия
        created_lessons = []
        for week in range(4):  # На 3 недели вперед
            lesson_date = data['datetime'] + timedelta(weeks=week)

            lesson = ScheduleElement.objects.create(
                teacher=teacher,
                student=student,
                exam=exam,
                lesson_name=data['lesson_name'],
                datetime=lesson_date,
                duration=data['duration'],
                teacher_comment=data.get('teacher_comment'),
                color=data.get('color', '#3b82f6'),
                is_repetitive=True,
                #recurring_template=recurring_element
            )
            if 'lesson_cost' in data:
                lesson.lesson_cost = data['lesson_cost']
                lesson.save()

            created_lessons.append(lesson)

        return created_lessons[0]  # Возвращаем первое занятие для ответа