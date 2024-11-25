from rest_framework import serializers
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
        Task = Variant
        fields = '__all__'

class TypeOfTaskSerializer(serializers.ModelSerializer):
    class Meta:
        Task = Variant
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        Task = Exam
        fields = '__all__'

class TeachersVariantStudentSerializer(serializers.ModelSerializer):
    class Meta:
        Task = TeachersVariantStudent
        fields = '__all__'
