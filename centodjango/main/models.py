from datetime import datetime
from django.db import models
from django.db.models import DateTimeField


class TeachersVariantStudent(models.Model):
    fk_teacher_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='teacher_v_s')
    fk_student_id = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='student_t_v')
    fk_variant_id = models.ForeignKey('Variant', on_delete=models.PROTECT, related_name='variant_t_s')
    dead_line = models.DateTimeField('Дедлайн')

    def __str__(self):
        return 'Связь, учителя ученика и варианта'

class Exam(models.Model):
    exam_id = models.CharField('Код экзамина', max_length=10, primary_key=True)
    exam_name = models.CharField('Название экзамена', max_length=128)

    def __str__(self):
        return 'Экзамен'

class TypeOfTask(models.Model):
    code_of_type = models.CharField('Код типа', max_length=10, primary_key=True)
    points = models.IntegerField('Баллы')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

    def __str__(self):
        return 'Баллы за номер'

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
        return 'Номер'

class Variant(models.Model):
    variant_id = models.CharField('Код варианта', max_length=10, primary_key=True)
    creator_id = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='variant_creator')
    visibility = models.BooleanField('Доступность')
    time_limit = models.TimeField('Временное ограничение')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT, related_name='exam_v')
    tasks = models.ManyToManyField(Task, related_name='TeacherToStudent')

    def __str__(self):
        return 'Вариант'

class Tariff(models.Model):
    tariff_id = models.CharField('Код тарифа', max_length=10, primary_key=True)
    tariff_name = models.CharField('Название тарифа', max_length=128)
    price = models.FloatField('Цена тарифа')
    tariff_info = models.TextField('Информация о тарифе')

    def __str__(self):
        return 'Тариф'

class Student(models.Model):
    student_id = models.CharField('Код ученика', max_length=10, primary_key=True)
    hash_password = models.CharField('Хэш пароля', max_length=32)
    name = models.CharField('Имя', max_length=32, default='nam')
    surname = models.CharField('Фамилия', max_length=32, default='sur')
    email = models.CharField('Почта', max_length=128)
    studying_year = models.IntegerField('Год обучения')

    def __str__(self):
        return 'Ученик'

class Teacher(models.Model):
    teacher_id = models.CharField('Код учителя', max_length=10, primary_key=True)
    name = models.CharField('Имя', max_length=32, default='nam')
    surname = models.CharField('Фамилия', max_length=32, default='sur')
    hash_password = models.CharField('Хэш пароля', max_length=128)
    email = models.CharField('Почта', max_length=128, default='em')
    tariff_end_date = DateTimeField('Конец Тарифа')
    fk_tariff_id = models.ForeignKey('Tariff', on_delete=models.PROTECT)
    students = models.ManyToManyField(Student, related_name='TeacherToStudent')
    exams = models.ManyToManyField(Exam, related_name='TeacherToExam')

    def __str__(self):
        return 'Учитель'