from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TypeOfTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfTask
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class TeachersVariantStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachersVariantStudent
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ('username', 'email', 'password', 'role', 'phone_number')

    def create(self, validated_data):
        role = validated_data.pop('role')
        validated_data['password'] = make_password(validated_data['password'])
        user = Account.objects.create(**validated_data)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        # Получаем стандартные данные (access и refresh токены)
        data = super().validate(attrs)
        # Добавляем роль пользователя в ответ
        data['role'] = self.user.role
        return data

class RoleBasedRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ('username', 'email', 'password', 'phone_number')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)



class LessonSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(write_only=True)  # Поле для email ученика

    class Meta:
        model = Lesson
        fields = ['id', 'teacher', 'student', 'datetime', 'student_email']
        read_only_fields = ['id', 'teacher', 'student']  # Эти поля заполняются автоматически

    def validate_student_email(self, value):
        """
        Проверяем, что ученик с указанным email существует и является учеником.
        """
        try:
            student_account = Account.objects.get(email=value, role='ученик')
            student = Student.objects.get(account=student_account)
            return student
        except Account.DoesNotExist:
            raise serializers.ValidationError("Ученик с указанным email не найден.")
        except Student.DoesNotExist:
            raise serializers.ValidationError("Ученик с указанным email не найден.")

    def validate(self, data):
        """
        Проверяем, что ученик принадлежит учителю, который создает урок.
        """
        user = self.context['request'].user
        if user.role != 'учитель':
            raise serializers.ValidationError("Только учитель может создавать уроки.")

        teacher = user.teacher
        student = data['student_email']  # student_email уже проверен в validate_student_email

        if not teacher.students.filter(id=student.id).exists():
            raise serializers.ValidationError("Ученик не найден в списке ваших учеников.")

        # Убираем student_email из данных, так как он больше не нужен
        data.pop('student_email')
        data['student'] = student  # Добавляем объект студента в данные

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        teacher = user.teacher

        lesson = Lesson.objects.create(
            teacher=teacher,
            **validated_data
        )
        return lesson



class ScheduleElementSerializer(serializers.ModelSerializer):
    teacher_info = serializers.SerializerMethodField()
    student_info = serializers.SerializerMethodField()
    exam_info = serializers.SerializerMethodField()

    class Meta:
        model = ScheduleElement
        fields = '__all__'

    def get_teacher_info(self, obj):
        return {
            'id': obj.teacher.id,
            'name': obj.teacher.account.username
        }

    def get_student_info(self, obj):
        return {
            'id': obj.student.id,
            'name': obj.student.account.username
        }

    def get_exam_info(self, obj):
        if obj.exam:
            return {
                'id': obj.exam.id,
                'name': obj.exam.exam_name
            }
        return None


class RecurringScheduleElementSerializer(serializers.ModelSerializer):
    teacher_info = serializers.SerializerMethodField()
    student_info = serializers.SerializerMethodField()
    exam_info = serializers.SerializerMethodField()
    next_occurrences = serializers.SerializerMethodField()

    class Meta:
        model = RecurringScheduleElement
        fields = '__all__'

    def get_teacher_info(self, obj):
        return {
            'id': obj.teacher.id,
            'name': obj.teacher.account.username
        }

    def get_student_info(self, obj):
        return {
            'id': obj.student.id,
            'name': obj.student.account.username
        }

    def get_exam_info(self, obj):
        if obj.exam:
            return {
                'id': obj.exam.id,
                'name': obj.exam.exam_name
            }
        return None

    def get_next_occurrences(self, obj):
        return ScheduleElement.objects.filter(
            recurring_template=obj,
            datetime__gte=datetime.now()
        ).values('id', 'datetime')[:5]  # Ближайшие 5 занятий


class ScheduleElementCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(write_only=True)
    exam_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    is_repetitive = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = ScheduleElement
        fields = [ 'student_id', 'exam_id', 'lesson_name', 'datetime', 'duration', 'teacher_comment', 'is_repetitive', 'color']
        extra_kwargs = {
            'teacher_comment': {'required': False},
            'color': {'required': False, 'default': '#3b82f6'}
        }

    def validate(self, data):
        if data['datetime'].replace(tzinfo=None) < datetime.now():
            raise serializers.ValidationError("Нельзя создавать занятия в прошлом")

        return data

