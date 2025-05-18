from datetime import datetime
from datetime import timedelta, timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import DateTimeField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class TeachersVariantStudent(models.Model):
    fk_teacher_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='teacher_v_s')
    fk_student_id = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='student_t_v')
    fk_variant_id = models.ForeignKey('Variant', on_delete=models.PROTECT, related_name='variant_t_s')
    dead_line = models.DateTimeField('Дедлайн')
    status = models.CharField(
        max_length=20,
        choices=[('задано', 'Задано'), ('на проверке', 'На проверке'), ('проверено', 'Проверено'), ('решено', 'Решено')],
        default='задано'
    )
    earned_points = models.IntegerField('Заработанные баллы', null=True, blank=True, default=0)

    def __str__(self):
        return f"Учитель: {self.fk_teacher_id}, Ученик: {self.fk_student_id}, Вариант: {self.fk_variant_id}"


class Exam(models.Model):
    exam_name = models.CharField('Название экзамена', max_length=128)

    def __str__(self):
        return self.exam_name


class TypeOfTask(models.Model):
    number_of_task = models.IntegerField('Номер задание')
    points = models.IntegerField('Баллы')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.id)


class Task(models.Model):
    fk_code_of_type = models.ForeignKey('TypeOfTask', on_delete=models.PROTECT, related_name='code_of_number')
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='task_creator', null=True, blank=True)
    visibility = models.BooleanField('Доступность')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_task')
    description = models.TextField('Описание задания')
    image_path = models.CharField('Путь до изображения', max_length=128, blank=True, null=True)
    correct_answer = models.CharField('Правильный ответ', max_length=128)
    file_path = models.CharField('Путь до файла', max_length=128, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Variant(models.Model):
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='variant_creator', null=True, blank=True)
    visibility = models.BooleanField('Доступность')
    time_limit = models.TimeField('Временное ограничение', null=True)
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_v')
    tasks = models.ManyToManyField(Task, related_name='TeacherToStudent')

    def __str__(self):
        return str(self.id)


class Tariff(models.Model):
    tariff_name = models.CharField('Название тарифа', max_length=128)
    price = models.FloatField('Цена тарифа')
    tariff_info = models.TextField('Информация о тарифе')

    def __str__(self):
        return self.tariff_name


class Account(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('ученик', 'Ученик'), ('учитель', 'Учитель')])
    # Указываем уникальные related_name для groups и user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="account_groups",  # Уникальное имя для обратной ссылки
        related_query_name="account",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="account_user_permissions",  # Уникальное имя для обратной ссылки
        related_query_name="account",
    )

    def __str__(self):
        return self.username


class Student(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='student', default=None)
    studying_year = models.IntegerField('Год обучения')
    exams = models.ManyToManyField('Exam', related_name='student_exams')

    def __str__(self):
        return self.account.username


class Teacher(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='teacher', default=None)
    tariff_end_date = models.DateTimeField('Конец Тарифа', blank=True, null=True)
    fk_tariff_id = models.ForeignKey('Tariff', on_delete=models.PROTECT, related_name='teacher_tariff')
    students = models.ManyToManyField('Student', related_name='teacher_students')
    exams = models.ManyToManyField('Exam', related_name='teacher_exams')
    education = models.TextField('Образование')

    def __str__(self):
        return self.account.username


class Lesson(models.Model):
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='lessons_taught')
    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='lessons_attended')
    datetime = models.DateTimeField('Дата и время занятия', default=datetime.now)

    def __str__(self):
        return f"Урок с учителем {self.teacher.account.username} для ученика {self.student.account.username} на {self.datetime}"


class RecurringScheduleElement(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    exam = models.ForeignKey( 'Exam', on_delete=models.PROTECT, null=True, blank=True, related_name='recurring_schedule_elements')
    lesson_name = models.CharField('Название урока', max_length=128)
    day_of_week = models.IntegerField( 'День недели', choices=DAYS_OF_WEEK, validators=[MinValueValidator(0), MaxValueValidator(6)])
    time = models.TimeField('Время начала урока')
    student = models.ForeignKey( 'Student', on_delete=models.PROTECT, related_name='recurring_schedule_elements')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='recurring_schedule_elements')
    color = models.CharField( 'Цвет', max_length=7, default='#3b82f6')
    duration = models.PositiveIntegerField('Длительность занятия (минуты)', default=60,)

    class Meta:
        verbose_name = 'Шаблон повторяющегося занятия'
        verbose_name_plural = 'Шаблоны повторяющихся занятий'
        unique_together = ['day_of_week', 'time', 'student', 'teacher']
        ordering = ['day_of_week', 'time']

    def __str__(self):
        return f"{self.lesson_name} ({self.time})"



class ScheduleElement(models.Model):
    # Основные поля
    exam = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='lessons', null=True, blank=True)
    lesson_name = models.CharField('Название урока', max_length=128)
    datetime = models.DateTimeField('Дата и время урока')
    is_repetitive = models.BooleanField('Повторяющееся занятие', default=False)

    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='scheduled_lessons_attended')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='scheduled_lessons_taught')

    color = models.CharField('Цвет', max_length=7, default='#bafd71')
    teacher_comment = models.TextField('Комментарий учителя', blank=True, null=True)
    student_comment = models.TextField('Комментарий ученика', blank=True, null=True)
    duration = models.PositiveIntegerField('Длительность занятия (минуты)', default=60, )

    # Статус урока
    STATUS_CHOICES = [
        ('not_held', 'Не проведено'),
        ('held', 'Проведено'),
        ('canceled_teacher', 'Отменено учителем'),
        ('canceled_student', 'Отменено учеником'),
    ]
    status = models.CharField('Статус урока', max_length=20, choices=STATUS_CHOICES, default='not_held')
    recurring_template = models.ForeignKey(
        RecurringScheduleElement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_elements',
        verbose_name='Шаблон повторяющегося занятия')


    PAYMENT_STATUS_CHOICES = [('paid', 'оплачено'), ('not_paid', 'не оплачено')]
    payment_status = models.CharField('Статус оплаты', max_length=20, choices=PAYMENT_STATUS_CHOICES,
                                      default='not_paid')
    lesson_cost = models.DecimalField('Стоимость задания', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.lesson_name} ({self.datetime})"

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'

