from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schools/', views.school_list, name='school_list'),
    path('schools/add/', views.add_school, name='add_school'),
    path('schools/edit/<int:school_id>/', views.edit_school, name='edit_school'),
    path('schools/delete/<int:school_id>/', views.delete_school, name='delete_school'),
    path('add_subjects/', views.add_subjects, name='add_subjects'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('edit_teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('assign_teacher/', views.assign_teacher, name='assign_teacher'),
    path('delete_assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('generate_timetable/', views.generate_timetable, name='generate_timetable'),
    path('get_teachers_for_class/', views.get_teachers_for_class, name='get_teachers_for_class'),
]