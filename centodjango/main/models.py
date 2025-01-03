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
    exam_id = models.CharField('Код экзамина', max_length=10, primary_key=True)
    exam_name = models.CharField('Название экзамена', max_length=128)

    def __str__(self):
        return self.exam_name

class TypeOfTask(models.Model):
    code_of_type = models.CharField('Код типа', max_length=10, primary_key=True)
    points = models.IntegerField('Баллы')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

    def __str__(self):
        return self.code_of_type

class Task(models.Model):
    task_id = models.CharField('Код номера', max_length=10, primary_key=True)
    fk_code_of_type = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='code_of_number')
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='task_creator', default='112211')
    visibility = models.BooleanField('Доступность')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_task')
    description = models.TextField('Описание задания')
    image_path = models.CharField('Путь до изображения', max_length=128)
    correct_answer = models.CharField('Правильный ответ', max_length=128)
    file_path = models.CharField('Путь до файла', max_length=128, default='113311')

    def __str__(self):
        return self.task_id

class Variant(models.Model):
    variant_id = models.CharField('Код варианта', max_length=10, primary_key=True)
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='variant_creator')
    visibility = models.BooleanField('Доступность')
    time_limit = models.TimeField('Временное ограничение')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_v')
    tasks = models.ManyToManyField(Task, related_name='TeacherToStudent')

    def __str__(self):
        return self.variant_id

class Tariff(models.Model):
    tariff_id = models.CharField('Код тарифа', max_length=10, primary_key=True)
    tariff_name = models.CharField('Название тарифа', max_length=128)
    price = models.FloatField('Цена тарифа')
    tariff_info = models.TextField('Информация о тарифе')

    def __str__(self):
        return self.tariff_name


class Account(AbstractUser):
    # Общие поля
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('student', 'Ученик'), ('teacher', 'Учитель')])
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

    def __str__(self):
        return self.account.username


class Teacher(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='teacher', default=None)
    tariff_end_date = models.DateTimeField('Конец Тарифа', blank=True, null=True)
    fk_tariff_id = models.ForeignKey('Tariff', on_delete=models.PROTECT, related_name='teacher_tariff')
    students = models.ManyToManyField('Student', related_name='teacher_students')
    exams = models.ManyToManyField('Exam', related_name='teacher_exams')

    def __str__(self):
        return self.account.username


@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            Student.objects.create(account=instance)
        elif instance.role == 'teacher':
            Teacher.objects.create(account=instance)

@receiver(post_save, sender=Account)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'student':
        instance.student.save()
    elif instance.role == 'teacher':
        instance.teacher.save()

