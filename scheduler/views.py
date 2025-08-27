from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import SubjectMaster, TeacherMaster, TeacherClassSubject, Timetable,SchoolMaster
from .forms import SubjectForm, TeacherForm, TeacherAssignmentForm,SchoolForm
from django.shortcuts import get_object_or_404
import json
from collections import defaultdict

import random
from datetime import datetime, timedelta


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


def assign_teacher(request):
    if request.method == 'POST':
        form = TeacherAssignmentForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            classes = form.cleaned_data['classes']
            
            assignments_created = 0
            invalid_assignments = 0
            
            for class_id in classes:
                subjects_key = f'subjects_class_{class_id}'
                if subjects_key in request.POST:
                    subject_ids = request.POST.getlist(subjects_key)
                    for subject_id in subject_ids:
                        try:
                            subject = SubjectMaster.objects.get(id=subject_id, class_id=class_id)
                            
                            # Check if teacher is already assigned to this class for a different subject
                            existing_assignment = TeacherClassSubject.objects.filter(
                                teacher=teacher, 
                                class_id=class_id
                            ).exclude(subject=subject).first()
                            
                            if existing_assignment:
                                messages.warning(request, 
                                    f"Teacher {teacher.name} is already assigned to {existing_assignment.subject.subject_name} in Class {class_id}. "
                                    f"Cannot assign to {subject.subject_name} in the same class."
                                )
                                invalid_assignments += 1
                                continue
                            
                            obj, created = TeacherClassSubject.objects.get_or_create(
                                teacher=teacher,
                                class_id=class_id,
                                subject=subject
                            )
                            if created:
                                assignments_created += 1
                                
                        except SubjectMaster.DoesNotExist:
                            invalid_assignments += 1
            
            if assignments_created > 0:
                messages.success(request, f"Successfully created {assignments_created} assignments!")
            if invalid_assignments > 0:
                messages.warning(request, f"{invalid_assignments} assignments could not be created due to conflicts.")
            
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
        
        # Get school information
        try:
            school = SchoolMaster.objects.first()
        except:
            school = None
        
        # Clear existing timetable for this class
        Timetable.objects.filter(class_id=class_id).delete()
        
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
        
        # Track teacher assignments
        teacher_assignments_track = defaultdict(list)  # Track assigned periods per teacher
        teacher_period_count = defaultdict(int)  # Count total periods per teacher
        
        # Create all possible slots (day, period) for the week
        all_slots = []
        for day in days:
            for period in range(1, periods_per_day[day] + 1):
                all_slots.append((day, period))
        
        # Shuffle slots for random assignment
        random.shuffle(all_slots)
        
        # For each subject, assign to periods
        for subject in subjects:
            if subject.id in subject_teachers:
                available_teachers = subject_teachers[subject.id]
                
                # Determine how many periods this subject should have per week
                subject_periods = getattr(subject, "periods_per_week", 3)
                
                assigned_periods = 0
                
                # Try to assign this subject to periods
                for day, period in all_slots:
                    if assigned_periods >= subject_periods:
                        break
                    
                    # Skip if slot already filled
                    if timetable_data[day][period]['subject'] != 'Free':
                        continue
                    
                    # Find suitable teacher for this period considering shift constraints
                    suitable_teachers = []
                    for teacher in available_teachers:
                        # Check shift constraints
                        if teacher.shift == 1 and period > 3:  # 1st shift teachers only in periods 1-3
                            continue
                        if teacher.shift == 2 and period <= 3:  # 2nd shift teachers only in periods 4-6
                            continue
                        
                        # Check if teacher hasn't exceeded their weekly limit
                        if teacher_period_count[teacher.id] >= teacher.no_of_classes:
                            continue
                        
                        # Check if teacher is already assigned in this period (across all classes)
                        teacher_key = f"{teacher.id}_{day}_{period}"
                        if teacher_key in teacher_assignments_track:
                            continue
                        
                        suitable_teachers.append(teacher)
                    
                    if not suitable_teachers:
                        continue
                    
                    # Pick the least loaded suitable teacher
                    teacher = min(suitable_teachers, key=lambda t: teacher_period_count[t.id])
                    
                    # Assign subject with this teacher
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
                    
                    # Update tracking
                    teacher_key = f"{teacher.id}_{day}_{period}"
                    teacher_assignments_track[teacher_key] = True
                    teacher_period_count[teacher.id] += 1
                    assigned_periods += 1
        
        # Create a matrix for easier template access
        periods = list(range(1, 7))
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
    classes_with_subjects = SubjectMaster.objects.values_list('class_id', flat=True).distinct()
    class_choices = [(cid, f"Class {cid}") for cid in sorted(classes_with_subjects)]
    
    teachers = TeacherMaster.objects.all()
    
    try:
        school = SchoolMaster.objects.first()
    except:
        school = None
    
    return render(request, 'scheduler/generate_timetable.html', {
        'classes': class_choices,
        'teachers': teachers,
        'school': school
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
def validate_timetable_constraints(class_id):
    """Validate that timetable meets all constraints"""
    timetable_entries = Timetable.objects.filter(class_id=class_id)
    teacher_assignments = defaultdict(list)
    
    for entry in timetable_entries:
        # Check teacher shift constraints
        if not entry.teacher.can_teach_in_period(entry.period_no):
            return False, f"Teacher {entry.teacher.name} (shift {entry.teacher.get_shift_display()}) assigned to invalid period {entry.period_no}"
        
        # Check teacher period conflicts (same teacher in same period across classes)
        conflict = Timetable.objects.filter(
            teacher=entry.teacher,
            day=entry.day,
            period_no=entry.period_no
        ).exclude(class_id=class_id).exists()
        
        if conflict:
            return False, f"Teacher {entry.teacher.name} has conflict in {entry.day} period {entry.period_no}"
        
        # Track teacher assignments
        teacher_assignments[entry.teacher.id].append((entry.day, entry.period_no))
    
    # Check teacher weekly limits
    for teacher_id, assignments in teacher_assignments.items():
        teacher = TeacherMaster.objects.get(id=teacher_id)
        if len(assignments) > teacher.no_of_classes:
            return False, f"Teacher {teacher.name} exceeds weekly limit ({len(assignments)}/{teacher.no_of_classes})"
    
    return True, "Timetable meets all constraints"
def teacher_routine(request):
    """Show all teachers with their weekly schedule summary"""
    # Get all teachers
    teachers = TeacherMaster.objects.all().order_by('name')
    
    # Get all timetable entries
    timetable_entries = Timetable.objects.all().select_related('teacher', 'subject')
    
    # Create teacher schedule summary with teacher ID as key
    teacher_schedules = {}
    over_assigned_count = 0
    under_utilized_count = 0
    
    for teacher in teachers:
        teacher_entries = [entry for entry in timetable_entries if entry.teacher == teacher]
        total_periods = len(teacher_entries)
        
        # Count statistics
        if total_periods > teacher.no_of_classes:
            over_assigned_count += 1
        elif total_periods < teacher.no_of_classes:
            under_utilized_count += 1
        
        # Count periods per day
        periods_per_day = {}
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            periods_per_day[day] = sum(1 for entry in teacher_entries if entry.day == day)
        
        teacher_schedules[teacher.id] = {
            'total_periods': total_periods,
            'periods_per_day': periods_per_day,
            'classes_taught': sorted(set(entry.class_id for entry in teacher_entries)),
            'subjects_taught': list(set(entry.subject for entry in teacher_entries)),
            'remaining_capacity': max(0, teacher.no_of_classes - total_periods),
            'teacher_obj': teacher  # Include teacher object for reference
        }
    
    return render(request, 'scheduler/teacher_routine.html', {
        'teachers': teachers,
        'teacher_schedules': teacher_schedules,
        'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'timetable_entries_count': timetable_entries.count(),
        'over_assigned_teachers': over_assigned_count,
        'under_utilized_teachers': under_utilized_count
    })

def teacher_detail_routine(request, teacher_id):
    """Show detailed routine for a specific teacher"""
    teacher = get_object_or_404(TeacherMaster, id=teacher_id)
    
    # Get all timetable entries for this teacher
    timetable_entries = Timetable.objects.filter(teacher=teacher).select_related('subject').order_by('day', 'period_no')
    
    # Create detailed schedule structure
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    schedule = {day: {} for day in days}
    
    for entry in timetable_entries:
        if entry.day in schedule:
            schedule[entry.day][entry.period_no] = {
                'class_id': entry.class_id,
                'subject': entry.subject.subject_name,
                'subject_id': entry.subject.id
            }
    
    # Fill empty periods
    for day in days:
        for period in range(1, 7):  # 6 periods
            if period not in schedule[day]:
                schedule[day][period] = {'class_id': None, 'subject': 'Free', 'subject_id': None}
    
    # Get teacher statistics
    total_periods = timetable_entries.count()
    classes_taught = set(entry.class_id for entry in timetable_entries)
    subjects_taught = set(entry.subject for entry in timetable_entries)
    
    return render(request, 'scheduler/teacher_detail_routine.html', {
        'teacher': teacher,
        'schedule': schedule,
        'days': days,
        'periods': range(1, 7),
        'total_periods': total_periods,
        'classes_taught': classes_taught,
        'subjects_taught': subjects_taught,
        'remaining_capacity': max(0, teacher.no_of_classes - total_periods)
    })
def teacher_routine(request):
    """Simple teacher routine overview without complex data structures"""
    teachers = TeacherMaster.objects.all().order_by('name')
    
    # Add simple calculated properties
    for teacher in teachers:
        total_periods = Timetable.objects.filter(teacher=teacher).count()
        teacher.total_periods = total_periods
        teacher.remaining_capacity = max(0, teacher.no_of_classes - total_periods)
    
    # Calculate statistics
    over_assigned_count = sum(1 for teacher in teachers if teacher.total_periods > teacher.no_of_classes)
    under_utilized_count = sum(1 for teacher in teachers if teacher.total_periods < teacher.no_of_classes)
    
    return render(request, 'scheduler/teacher_routine.html', {
        'teachers': teachers,
        'timetable_entries_count': Timetable.objects.count(),
        'over_assigned_teachers': over_assigned_count,
        'under_utilized_teachers': under_utilized_count
    })
def teacher_detail_routine(request, teacher_id):
    """Show detailed routine for a specific teacher across all classes"""
    teacher = get_object_or_404(TeacherMaster, id=teacher_id)
    
    # Get date range for the week
    today = timezone.now().date()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=5)
    
    # Get all timetable entries
    timetable_entries = Timetable.objects.filter(
        teacher=teacher
    ).select_related('subject').order_by('day', 'period_no', 'class_id')
    
    # Simple data structure for template
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    periods = range(1, 7)
    
    # Create a simple list of entries for the template
    schedule_entries = []
    for entry in timetable_entries:
        schedule_entries.append({
            'day': entry.day,
            'period': entry.period_no,
            'class_id': entry.class_id,
            'subject': entry.subject.subject_name,
            'has_shift_conflict': (
                (teacher.shift == 1 and entry.period_no > 3) or
                (teacher.shift == 2 and entry.period_no <= 3)
            )
        })
    
    # Statistics
    total_periods = timetable_entries.count()
    classes_taught = sorted(set(entry.class_id for entry in timetable_entries))
    subjects_taught = list(set(entry.subject.subject_name for entry in timetable_entries))
    
    return render(request, 'scheduler/teacher_detail_routine.html', {
        'teacher': teacher,
        'schedule_entries': schedule_entries,
        'days': days,
        'periods': periods,
        'start_date': start_date,
        'end_date': end_date,
        'total_periods': total_periods,
        'classes_taught': classes_taught,
        'subjects_taught': subjects_taught,
        'remaining_capacity': max(0, teacher.no_of_classes - total_periods)
    })