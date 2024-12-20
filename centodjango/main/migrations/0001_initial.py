# Generated by Django 5.1.1 on 2024-11-25 12:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('exam_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код экзамина')),
                ('exam_name', models.CharField(max_length=128, verbose_name='Название экзамена')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код ученика')),
                ('hash_password', models.CharField(max_length=32, verbose_name='Хэш пароля')),
                ('name', models.CharField(default='nam', max_length=32, verbose_name='Имя')),
                ('surname', models.CharField(default='sur', max_length=32, verbose_name='Фамилия')),
                ('email', models.CharField(max_length=128, verbose_name='Почта')),
                ('studying_year', models.IntegerField(verbose_name='Год обучения')),
            ],
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('tariff_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код тарифа')),
                ('tariff_name', models.CharField(max_length=128, verbose_name='Название тарифа')),
                ('price', models.FloatField(verbose_name='Цена тарифа')),
                ('tariff_info', models.TextField(verbose_name='Информация о тарифе')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('teacher_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код учителя')),
                ('name', models.CharField(default='nam', max_length=32, verbose_name='Имя')),
                ('surname', models.CharField(default='sur', max_length=32, verbose_name='Фамилия')),
                ('hash_password', models.CharField(max_length=128, verbose_name='Хэш пароля')),
                ('email', models.CharField(default='em', max_length=128, verbose_name='Почта')),
                ('tariff_end_date', models.DateTimeField(verbose_name='Конец Тарифа')),
                ('exams', models.ManyToManyField(related_name='TeacherToExam', to='main.exam')),
                ('fk_tariff_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.tariff')),
                ('students', models.ManyToManyField(related_name='TeacherToStudent', to='main.student')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('task_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код номера')),
                ('visibility', models.BooleanField(verbose_name='Доступность')),
                ('description', models.TextField(verbose_name='Описание задания')),
                ('image_path', models.CharField(max_length=128, verbose_name='Путь до изображения')),
                ('correct_answer', models.CharField(max_length=128, verbose_name='Правильный ответ')),
                ('file_path', models.CharField(default='113311', max_length=128, verbose_name='Путь до файла')),
                ('fk_code_of_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='code_of_number', to='main.exam')),
                ('fk_exam_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exam_task', to='main.exam')),
                ('creator_id', models.ForeignKey(default='112211', on_delete=django.db.models.deletion.PROTECT, related_name='task_creator', to='main.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TypeOfTask',
            fields=[
                ('code_of_type', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код типа')),
                ('points', models.IntegerField(verbose_name='Баллы')),
                ('fk_exam_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.exam')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('variant_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код варианта')),
                ('visibility', models.BooleanField(verbose_name='Доступность')),
                ('time_limit', models.TimeField(verbose_name='Временное ограничение')),
                ('creator_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='variant_creator', to='main.teacher')),
                ('fk_exam_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exam_v', to='main.exam')),
                ('tasks', models.ManyToManyField(related_name='TeacherToStudent', to='main.task')),
            ],
        ),
        migrations.CreateModel(
            name='TeachersVariantStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dead_line', models.DateTimeField(verbose_name='Дедлайн')),
                ('fk_student_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='student_t_v', to='main.student')),
                ('fk_teacher_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teacher_v_s', to='main.teacher')),
                ('fk_variant_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='variant_t_s', to='main.variant')),
            ],
        ),
    ]
