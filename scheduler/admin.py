from django.contrib import admin
from .models import SchoolMaster, SubjectMaster, TeacherMaster, TeacherClassSubject, Timetable

@admin.register(SchoolMaster)
class SchoolMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'address')
    search_fields = ('name', 'code')

@admin.register(SubjectMaster)
class SubjectMasterAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'subject_name')
    list_filter = ('class_id',)
    search_fields = ('subject_name',)

@admin.register(TeacherMaster)
class TeacherMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'shift', 'no_of_classes')
    list_filter = ('shift',)
    search_fields = ('name',)

@admin.register(TeacherClassSubject)
class TeacherClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'class_id', 'subject')
    list_filter = ('class_id', 'teacher')
    search_fields = ('teacher__name', 'subject__subject_name')

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'day', 'period_no', 'teacher', 'subject')
    list_filter = ('class_id', 'day', 'teacher')
    search_fields = ('teacher__name', 'subject__subject_name')