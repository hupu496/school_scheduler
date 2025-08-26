from django import forms
from .models import SubjectMaster, TeacherMaster, TeacherClassSubject,SchoolMaster


class SubjectForm(forms.Form):
    classes = forms.MultipleChoiceField(
        choices=SubjectMaster.CLASS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Classes"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 11):
            self.fields[f'subjects_class_{i}'] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={'placeholder': 'Enter subjects separated by commas'}),
                label=f"Subjects for Class {i}"
            )

class SchoolForm(forms.ModelForm):
    class Meta:
        model = SchoolMaster
        fields = ['name', 'code', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter school name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter school code'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter school address',
                'rows': 3
            }),
        }
        labels = {
            'name': 'School Name',
            'code': 'School Code',
            'address': 'School Address',
        }
class TeacherForm(forms.ModelForm):
    class Meta:
        model = TeacherMaster
        fields = ['name', 'shift', 'no_of_classes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter teacher name'
            }),
            'shift': forms.Select(attrs={
                'class': 'form-control'
            }),
            'no_of_classes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 40
            }),
        }
        labels = {
            'name': 'Teacher Name',
            'shift': 'Teaching Shift',
            'no_of_classes': 'Maximum Classes per Week',
        }

class TeacherAssignmentForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=TeacherMaster.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select a teacher'
        }),
        label="Teacher"
    )
    
    classes = forms.MultipleChoiceField(
        choices=SubjectMaster.CLASS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Classes"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = TeacherMaster.objects.all().order_by('name')