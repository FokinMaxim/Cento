from django.db import models


class TeachersVariantStudent(models.Model):
    fk_teacher_id = models.ForeignKey('Teacher', on_delete=models.PROTECT)
    fk_student_id = models.ForeignKey('Student', on_delete=models.PROTECT)
    fk_variant_id = models.ForeignKey('Variant', on_delete=models.PROTECT)
    dead_line = models.DateTimeField('Дедлайн')

    def __str__(self):
        return 'Связь, учителя ученика и варианта'

class VariantToTask(models.Model):
    fk_variant_id = models.ForeignKey('Variant', on_delete=models.PROTECT)
    fk_task_id = models.ForeignKey('Task', on_delete=models.PROTECT)

    def __str__(self):
        return 'Связь варианта и номера'

class TeachersToStudent(models.Model):
    fk_teacher_id = models.ForeignKey('Teacher', on_delete=models.PROTECT)
    fk_student_id = models.ForeignKey('Student', on_delete=models.PROTECT)

    def __str__(self):
        return 'Связь учителя и ученика'

class TeachersToExam(models.Model):
    fk_teacher_id = models.ForeignKey('Teacher', on_delete=models.PROTECT)
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

    def __str__(self):
        return 'Связь учителя и экзамена'

class Exam(models.Model):
    exam_id = models.CharField('Код экзамина', max_length=10, primary_key=True)
    exam_name = models.CharField('Название экзамена', max_length=128)

    def __str__(self):
        return 'Экзамен'

class PointsOfTask(models.Model):
    code_of_number = models.CharField('Код типа', max_length=10, primary_key=True)
    points = models.IntegerField('Баллы')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

    def __str__(self):
        return 'Баллы за номер'

class Task(models.Model):
    task_id = models.CharField('Код номера', max_length=10, primary_key=True)
    fk_code_of_number = models.ForeignKey('Exam', on_delete=models.PROTECT)
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)
    description = models.TextField('Описание задания')
    image_path = models.CharField('Путь до изображения', max_length=128)
    correct_answer = models.CharField('Правильный ответ', max_length=128)

    def __str__(self):
        return 'Номер'

class Variant(models.Model):
    variant_id = models.CharField('Код варианта', max_length=10, primary_key=True)
    creator_id = models.CharField('Код создателя', max_length=10)
    visibility = models.BooleanField('Доступность')
    time_limit = models.TimeField('Временное ограничение')
    fk_exam_id = models.ForeignKey('Exam', on_delete=models.PROTECT)

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
    hash_login = models.CharField('Хэш логина', max_length=128)
    hash_password = models.CharField('Хэш пароля', max_length=128)
    hash_email = models.CharField('Хэш почты', max_length=128)
    studying_year = models.IntegerField('Год обучения')

    def __str__(self):
        return 'Ученик'

class Teacher(models.Model):
    teacher_id = models.CharField('Код учителя', max_length=10, primary_key=True)
    hash_login = models.CharField('Хэш логина', max_length=128)
    hash_password = models.CharField('Хэш пароля', max_length=128)
    hash_email = models.CharField('Хэш почты', max_length=128)
    fk_tariff_id = models.ForeignKey('Tariff', on_delete=models.PROTECT)

    def __str__(self):
        return 'Учитель'