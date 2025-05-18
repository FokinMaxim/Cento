from django.contrib import admin
from .models import *

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('id', 'username', 'email')


class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'studying_year']
    list_filter = ('studying_year',)
    search_fields = ('id', 'account__username', 'account__email')


class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'tariff_end_date', 'fk_tariff_id']
    list_filter = ('tariff_end_date',)
    search_fields = ('id', 'account__username', 'account__email')


class VariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'creator_id', 'visibility', 'time_limit', 'fk_exam_id']
    list_display_links = ['id']
    search_fields = ['id', 'creator_id__account__username', 'visibility', 'time_limit', 'fk_exam_id__exam_name']
    list_filter = ['visibility', 'fk_exam_id']


class TariffAdmin(admin.ModelAdmin):
    list_display = ['id', 'tariff_name', 'price', 'tariff_info']
    list_display_links = ['id']
    search_fields = ['tariff_name', 'price', 'tariff_info']
    list_filter = ['tariff_name', 'price']


class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_code_of_type', 'creator_id', 'visibility', 'fk_exam_id', 'description', 'image_path', 'file_path']
    list_display_links = ['id']
    search_fields = ['id', 'fk_code_of_type__code_of_type', 'creator_id__account__username', 'visibility', 'fk_exam_id__exam_name', 'description']
    list_filter = ['visibility', 'fk_exam_id']


class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam_name']
    list_display_links = ['id']
    search_fields = ['exam_name']
    list_filter = ['exam_name']


class TypeOfTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'number_of_task', 'points', 'fk_exam_id']
    list_display_links = ['id']
    search_fields = ['points', 'fk_exam_id__exam_name']
    list_filter = ['fk_exam_id']


class TeachersVariantStudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_teacher_id', 'fk_student_id', 'fk_variant_id', 'dead_line', 'status']
    search_fields = ['fk_teacher_id__account__username', 'fk_student_id__account__username', 'fk_variant_id__id', 'dead_line']
    list_filter = ['fk_teacher_id', 'fk_student_id', 'fk_variant_id', 'dead_line', 'status']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'teacher', 'student', 'datetime']
    list_display_links = ['id']
    search_fields = ['teacher', 'student', 'datetime']
    list_filter = ['datetime']


class ScheduleElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson_name', 'teacher', 'student', 'datetime', 'status',
                    'is_repetitive', 'exam', 'payment_status', 'lesson_cost')
    list_display_links = ('id', 'lesson_name')
    list_filter = ('status', 'datetime', 'exam', 'teacher', 'student', 'payment_status')
    search_fields = ('lesson_name', 'teacher__account__username', 'student__account__username',
                     'exam__exam_name', 'teacher_comment', 'student_comment', 'payment_status', 'lesson_cost')



class RecurringScheduleElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'lesson_name', 'teacher', 'student', 'day_of_week', 'time')
    list_filter = ('day_of_week', 'exam', 'teacher')


admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(TypeOfTask, TypeOfTaskAdmin)
admin.site.register(TeachersVariantStudent, TeachersVariantStudentAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(ScheduleElement, ScheduleElementAdmin)
admin.site.register(RecurringScheduleElement, RecurringScheduleElementAdmin)