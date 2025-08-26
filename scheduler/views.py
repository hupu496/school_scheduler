from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from .models import SchoolMaster
from .models import SubjectMaster, TeacherMaster, TeacherClassSubject, Timetable
from .forms import SubjectForm, TeacherForm, TeacherAssignmentForm,SchoolForm
from django.shortcuts import get_object_or_404
import json
from collections import defaultdict
from datetime import datetime
import random

def index(request):
    return render(request, 'scheduler/index.html')
def school_list(request):
    schools = SchoolMaster.objects.all().order_by('name')
    return render(request, 'scheduler/school_list.html', {'schools': schools})

def add_school(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            school = form.save()
            messages.success(request, f"School '{school.name}' added successfully!")
            return redirect('school_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolForm()
    
    return render(request, 'scheduler/school_form.html', {
        'form': form,
        'title': 'Add New School'
    })

def edit_school(request, school_id):
    school = get_object_or_404(SchoolMaster, id=school_id)
    
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            school = form.save()
            messages.success(request, f"School '{school.name}' updated successfully!")
            return redirect('school_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolForm(instance=school)
    
    return render(request, 'scheduler/school_form.html', {
        'form': form,
        'title': 'Edit School',
        'school': school
    })

def delete_school(request, school_id):
    school = get_object_or_404(SchoolMaster, id=school_id)
    
    if request.method == 'POST':
        school_name = school.name
        school.delete()
        messages.success(request, f"School '{school_name}' deleted successfully!")
        return redirect('school_list')
    
    return render(request, 'scheduler/confirm_delete_school.html', {'school': school})
def add_subjects(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            classes = form.cleaned_data['classes']
            for class_id in classes:
                subjects_field = f'subjects_class_{class_id}'
                if subjects_field in form.cleaned_data and form.cleaned_data[subjects_field]:
                    subjects = [s.strip() for s in form.cleaned_data[subjects_field].split(',')]
                    for subject_name in subjects:
                        if subject_name:  # Skip empty strings
                            SubjectMaster.objects.get_or_create(
                                class_id=class_id,
                                subject_name=subject_name
                            )
            return redirect('index')
    else:
        form = SubjectForm()
    
    return render(request, 'scheduler/add_subjects.html', {'form': form})
def add_subjects(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            classes = form.cleaned_data['classes']
            created_count = 0
            
            for class_id in classes:
                subjects_field = f'subjects_class_{class_id}'
                if subjects_field in form.cleaned_data and form.cleaned_data[subjects_field]:
                    subjects = [s.strip() for s in form.cleaned_data[subjects_field].split(',')]
                    for subject_name in subjects:
                        if subject_name:  # Skip empty strings
                            obj, created = SubjectMaster.objects.get_or_create(
                                class_id=class_id,
                                subject_name=subject_name
                            )
                            if created:
                                created_count += 1
            
            messages.success(request, f"Successfully created {created_count} new subjects")
            return redirect('add_subjects')
    else:
        form = SubjectForm()
    
    # Get existing subjects grouped by class
    existing_subjects = {}
    for class_id in range(1, 11):
        subjects = SubjectMaster.objects.filter(class_id=class_id)
        if subjects.exists():
            existing_subjects[class_id] = subjects
    
    return render(request, 'scheduler/add_subjects.html', {
        'form': form,
        'existing_subjects': existing_subjects
    })

def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher '{teacher.name}' added successfully!")
            return redirect('add_teacher')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherForm()
    
    # Get all existing teachers
    existing_teachers = TeacherMaster.objects.all().order_by('name')
    
    return render(request, 'scheduler/add_teacher.html', {
        'form': form,
        'existing_teachers': existing_teachers
    })
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherMaster, id=teacher_id)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher '{teacher.name}' updated successfully!")
            return redirect('add_teacher')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherForm(instance=teacher)
    
    existing_teachers = TeacherMaster.objects.all().order_by('name')
    
    return render(request, 'scheduler/add_teacher.html', {
        'form': form,
        'existing_teachers': existing_teachers,
        'editing_teacher': teacher
    })

def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherMaster, id=teacher_id)
    
    if request.method == 'POST':
        teacher_name = teacher.name
        teacher.delete()
        messages.success(request, f"Teacher '{teacher_name}' deleted successfully!")
        return redirect('add_teacher')
    
    return render(request, 'scheduler/confirm_delete.html', {'teacher': teacher})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import TeacherClassSubject, TeacherMaster, SubjectMaster
from .forms import TeacherAssignmentForm

def assign_teacher(request):
    if request.method == 'POST':
        form = TeacherAssignmentForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            classes = form.cleaned_data['classes']
            
            assignments_created = 0
            # Get selected subjects for each class
            for class_id in classes:
                subjects_key = f'subjects_class_{class_id}'
                if subjects_key in request.POST:
                    subject_ids = request.POST.getlist(subjects_key)
                    for subject_id in subject_ids:
                        try:
                            subject = SubjectMaster.objects.get(id=subject_id, class_id=class_id)
                            obj, created = TeacherClassSubject.objects.get_or_create(
                                teacher=teacher,
                                class_id=class_id,
                                subject=subject
                            )
                            if created:
                                assignments_created += 1
                        except SubjectMaster.DoesNotExist:
                            pass
            
            if assignments_created > 0:
                messages.success(request, f"Successfully created {assignments_created} assignments!")
            else:
                messages.info(request, "No new assignments were created.")
            
            return redirect('assign_teacher')
    else:
        form = TeacherAssignmentForm()
    
    # Create a list of tuples with class_id and subjects
    class_subjects = []
    for class_id in range(1, 11):
        subjects = SubjectMaster.objects.filter(class_id=class_id)
        class_subjects.append((class_id, subjects))
    
    # Get all existing assignments
    existing_assignments = TeacherClassSubject.objects.all().select_related('teacher', 'subject').order_by('class_id', 'teacher__name')
    
    return render(request, 'scheduler/assign_teacher.html', {
        'form': form,
        'class_subjects': class_subjects,
        'existing_assignments': existing_assignments
    })

def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(TeacherClassSubject, id=assignment_id)
    
    if request.method == 'POST':
        assignment_info = f"{assignment.teacher.name} - Class {assignment.class_id} - {assignment.subject.subject_name}"
        assignment.delete()
        messages.success(request, f"Assignment '{assignment_info}' deleted successfully!")
        return redirect('assign_teacher')
    
    return render(request, 'scheduler/confirm_delete_assignment.html', {'assignment': assignment})

def get_subjects_for_class(request):
    class_id = request.GET.get('class_id')
    subjects = SubjectMaster.objects.filter(class_id=class_id)
    data = [{'id': s.id, 'name': s.subject_name} for s in subjects]
    return JsonResponse(data, safe=False)

def generate_timetable(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        class_teacher = request.POST.get('class_teacher', '')
        effective_date = request.POST.get('effective_date', '')
        
        # Clear existing timetable for this class
        Timetable.objects.filter(class_id=class_id).delete()
        try:
            school = SchoolMaster.objects.first()
        except:
            school = None
        # Get all subjects for this class
        subjects = SubjectMaster.objects.filter(class_id=class_id)
        
        # Get teachers who can teach these subjects for this class
        teacher_assignments = TeacherClassSubject.objects.filter(
            class_id=class_id, 
            subject__in=subjects
        ).select_related('teacher', 'subject')
        
        # Create a mapping of subject to available teachers
        subject_teachers = defaultdict(list)
        for assignment in teacher_assignments:
            subject_teachers[assignment.subject.id].append(assignment.teacher)
        
        # Create timetable structure
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        periods_per_day = {
            'Mon': 6, 'Tue': 6, 'Wed': 6, 'Thu': 6, 'Fri': 6, 'Sat': 4
        }
        
        # Initialize empty timetable
        timetable_data = {}
        for day in days:
            timetable_data[day] = {}
            for period in range(1, periods_per_day[day] + 1):
                timetable_data[day][period] = {'subject': 'Free', 'teacher': ''}
        
        # Track teacher assignments to avoid conflicts
        teacher_assignments_track = defaultdict(list)
        teacher_period_count = defaultdict(int)
        
        # Create all possible slots and shuffle them for random assignment
        all_slots = [(day, period) for day in days for period in range(1, periods_per_day[day] + 1)]
        random.shuffle(all_slots)
        
        # For each subject, assign to periods
        for subject in subjects:
            if subject.id in subject_teachers:
                available_teachers = subject_teachers[subject.id]
                # Get subject periods per week (default to 3 if not specified)
                subject_periods = getattr(subject, "periods_per_week", 3)

                assigned_periods = 0
                for day, period in all_slots:
                    if assigned_periods >= subject_periods:
                        break

                    # Skip if slot already filled
                    if timetable_data[day][period]['subject'] != 'Free':
                        continue

                    # Pick least-loaded teacher
                    teacher = min(
                        available_teachers, 
                        key=lambda t: teacher_period_count[t.id]
                    )

                    teacher_key = f"{teacher.id}_{day}_{period}"
                    if (teacher_key not in teacher_assignments_track and 
                        teacher_period_count[teacher.id] < teacher.no_of_classes):
                        
                        # Assign subject + teacher
                        timetable_data[day][period] = {
                            'subject': subject.subject_name,
                            'teacher': teacher.name
                        }

                        # Save to database
                        Timetable.objects.create(
                            class_id=class_id,
                            day=day,
                            period_no=period,
                            teacher=teacher,
                            subject=subject
                        )

                        teacher_assignments_track[teacher_key] = True
                        teacher_period_count[teacher.id] += 1
                        assigned_periods += 1
        
        # Create a matrix for easier template access
        periods = list(range(1, 7))  # 6 periods maximum
        timetable_matrix = []
        
        for period in periods:
            period_row = {'period': period, 'days': {}}
            for day in days:
                # For Saturday, only show periods 1-4
                if day == 'Sat' and period > 4:
                    period_row['days'][day] = {'subject': '-', 'teacher': ''}
                elif day in timetable_data and period in timetable_data[day]:
                    period_row['days'][day] = timetable_data[day][period]
                else:
                    period_row['days'][day] = {'subject': 'Free', 'teacher': ''}
            timetable_matrix.append(period_row)
       
        
        # Format the effective date
        if effective_date:
            try:
                date_obj = datetime.strptime(effective_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d.%m.%Y')
            except:
                formatted_date = datetime.now().strftime('%d.%m.%Y')
        else:
            formatted_date = datetime.now().strftime('%d.%m.%Y')
        
        return render(request, 'scheduler/timetable_result.html', {
            'class_id': class_id,
            'class_teacher': class_teacher,
            'effective_date': formatted_date,
            'timetable_matrix': timetable_matrix,
            'periods': periods,
            'days': days,
            'school': school
        })
    
    # For GET request, show form with available classes
    # Get all classes that have subjects defined
    classes_with_subjects = SubjectMaster.objects.values_list('class_id', flat=True).distinct()
    class_choices = [(cid, f"Class {cid}") for cid in sorted(classes_with_subjects)]
    
    # Get all teachers for the dropdown
    teachers = TeacherMaster.objects.all()
    
    # Get school information
    
    
    return render(request, 'scheduler/generate_timetable.html', {
        'classes': class_choices,
        'teachers': teachers,
        
    })

def get_teachers_for_class(request):
    """API endpoint to get teachers available for a specific class"""
    class_id = request.GET.get('class_id')

    teachers = (
        TeacherClassSubject.objects.filter(class_id=class_id)
        .values('teacher__id', 'teacher__name')
        .distinct()
    )

    teachers_list = [{'id': t['teacher__id'], 'name': t['teacher__name']} for t in teachers]

    return JsonResponse(teachers_list, safe=False)
