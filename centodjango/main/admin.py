from django.contrib import admin
from .models import *

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('username', 'email')


class StudentAdmin(admin.ModelAdmin):
    list_display = ['account', 'studying_year']
    list_filter = ('studying_year',)
    search_fields = ('account__username', 'account__email')

class TeacherAdmin(admin.ModelAdmin):
    list_display = ['account', 'tariff_end_date', 'fk_tariff_id']
    list_filter = ('tariff_end_date',)
    search_fields = ('account__username', 'account__email')

class VariantAdmin(admin.ModelAdmin):
    list_display = ['variant_id', 'creator_id', 'visibility', 'time_limit', 'fk_exam_id']
    list_display_links = ['variant_id']
    search_fields = ['variant_id', 'creator_id', 'visibility', 'time_limit', 'fk_exam_id']
    list_filter = ['variant_id', 'creator_id', 'visibility', 'time_limit', 'fk_exam_id']

class TariffAdmin(admin.ModelAdmin):
    list_display = ['tariff_id', 'tariff_name', 'price', 'tariff_info']
    list_display_links = ['tariff_id']
    search_fields = ['tariff_id', 'tariff_name', 'price', 'tariff_info']
    list_filter = ['tariff_id', 'tariff_name', 'price', 'tariff_info']

class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'fk_code_of_type', 'creator_id', 'visibility', 'fk_exam_id', 'description',
                    'image_path', 'correct_answer', 'file_path']
    list_display_links = ['task_id']
    search_fields = ['task_id', 'fk_code_of_type', 'creator_id', 'visibility', 'fk_exam_id', 'description',
                    'image_path', 'correct_answer', 'file_path']
    list_filter = ['task_id', 'fk_code_of_type', 'creator_id', 'visibility', 'fk_exam_id', 'description',
                    'image_path', 'correct_answer', 'file_path']

class ExamAdmin(admin.ModelAdmin):
    list_display = ['exam_id', 'exam_name']
    list_display_links = ['exam_id']
    search_fields = ['exam_id', 'exam_name']
    list_filter = ['exam_id', 'exam_name']

class TypeOfTaskAdmin(admin.ModelAdmin):
    list_display = ['code_of_type', 'points', 'fk_exam_id']
    list_display_links = ['code_of_type']
    search_fields = ['code_of_type', 'points', 'fk_exam_id']
    list_filter = ['code_of_type', 'points', 'fk_exam_id']

class TeachersVariantStudent(admin.ModelAdmin):
    list_display = ['fk_teacher_id', 'fk_student_id', 'fk_variant_id', 'dead_line']
    search_fields = ['fk_teacher_id', 'fk_student_id', 'fk_variant_id', 'dead_line']
    list_filter = ['fk_teacher_id', 'fk_student_id', 'fk_variant_id', 'dead_line']

admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(TypeOfTask, TypeOfTaskAdmin)