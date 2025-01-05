from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import DateTimeField
from django.db.models.signals import post_save
from django.dispatch import receiver


class TeachersVariantStudent(models.Model):
    fk_teacher_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='teacher_v_s')
    fk_student_id = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='student_t_v')
    fk_variant_id = models.ForeignKey('Variant', on_delete=models.PROTECT, related_name='variant_t_s')
    dead_line = models.DateTimeField('Дедлайн')

    def __str__(self):
        return f"Учитель: {self.fk_teacher_id}, Ученик: {self.fk_student_id}, Вариант: {self.fk_variant_id}"

class Exam(models.Model):
    exam_name = models.CharField('Название экзамена', max_length=128)

    def __str__(self):
        return self.exam_name

class TypeOfTask(models.Model):
    points = models.IntegerField('Баллы')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

    def __str__(self):
        return self.id

class Task(models.Model):
    fk_code_of_type = models.ForeignKey('TypeOfTask', on_delete=models.PROTECT, related_name='code_of_number')
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='task_creator', default='112211')
    visibility = models.BooleanField('Доступность')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_task')
    description = models.TextField('Описание задания')
    image_path = models.CharField('Путь до изображения', max_length=128)
    correct_answer = models.CharField('Правильный ответ', max_length=128)
    file_path = models.CharField('Путь до файла', max_length=128, default='113311')

    def __str__(self):
        return self.id

class Variant(models.Model):
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='variant_creator')
    visibility = models.BooleanField('Доступность')
    time_limit = models.TimeField('Временное ограничение')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_v')
    tasks = models.ManyToManyField(Task, related_name='TeacherToStudent')
    status = models.CharField(max_length=20,
                              choices=[ ('задано', 'Задано'),
                                        ('на проверке', 'На проверке'),
                                        ('проверено', 'Проверено'), ],
                              default='задано')

    def __str__(self):
        return self.id

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