# Generated by Django 5.1.1 on 2024-10-27 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='Код ученика')),
                ('hash_login', models.CharField(max_length=128, verbose_name='Хэш логина')),
                ('hash_password', models.CharField(max_length=128, verbose_name='Хэш пароля')),
                ('hash_email', models.CharField(max_length=128, verbose_name='Хэш почты')),
                ('studying_year', models.IntegerField(verbose_name='Год обучения')),
            ],
        ),
    ]
