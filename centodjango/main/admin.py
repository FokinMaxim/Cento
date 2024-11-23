from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'hash_password', 'name', 'surname', 'email', 'studying_year']
    list_display_links = ['student_id']
    search_fields = ['student_id', 'hash_password', 'name', 'surname', 'email', 'studying_year']
    list_filter = ['student_id', 'hash_password', 'name', 'surname', 'email', 'studying_year']

admin.site.register(Student, StudentAdmin)