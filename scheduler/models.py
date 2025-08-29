from django.db import models
from django.core.exceptions import ValidationError

class SchoolMaster(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class SubjectMaster(models.Model):
    CLASS_CHOICES = [(i, f"Class {i}") for i in range(1, 11)]
    
    class_id = models.IntegerField(choices=CLASS_CHOICES)
    subject_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('class_id', 'subject_name')
    
    def __str__(self):
        return f"Class {self.class_id} - {self.subject_name}"

class TeacherMaster(models.Model):
    SHIFT_CHOICES = [
        (1, "1st Shift (Classes 1-3)"),
        (2, "2nd Shift (Classes 4-6)"),
        (3, "All Shifts"),
    ]

    name = models.CharField(max_length=100)
    shift = models.IntegerField(choices=SHIFT_CHOICES)
    no_of_classes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Shift {self.get_shift_display()})"

    def clean(self):
        # Validate that no_of_classes is reasonable
        if self.no_of_classes < 0:
            raise ValidationError({'no_of_classes': ['Number of classes cannot be negative.']})
        if self.no_of_classes > 40:  # Assuming 40 periods per week maximum
            raise ValidationError({'no_of_classes': ['Number of classes cannot exceed 40 per week.']})

    def save(self, *args, **kwargs):
        # Ensure clean() is always called before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_remaining_capacity(self):
        """Get remaining teaching capacity for this teacher"""
        total_assigned = Timetable.objects.filter(teacher=self).count()
        return max(0, self.no_of_classes - total_assigned)
    
    def can_teach_in_period(self, period):
        """Check if teacher can teach in given period based on shift"""
        if self.shift == 1:  # 1st shift - only periods 1-3
            return period <= 3
        elif self.shift == 2:  # 2nd shift - only periods 4-6
            return period >= 4
        else:  # All shifts - any period
            return True

class TeacherClassSubject(models.Model):
    teacher = models.ForeignKey(TeacherMaster, on_delete=models.CASCADE)
    class_id = models.IntegerField(choices=SubjectMaster.CLASS_CHOICES)
    subject = models.ForeignKey(SubjectMaster, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('teacher', 'class_id', 'subject')
    
    def __str__(self):
        return f"{self.teacher.name} - Class {self.class_id} - {self.subject.subject_name}"

class Timetable(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday')
    ]
    
    class_id = models.IntegerField(choices=SubjectMaster.CLASS_CHOICES)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    period_no = models.IntegerField()
    teacher = models.ForeignKey(TeacherMaster, on_delete=models.CASCADE)
    subject = models.ForeignKey(SubjectMaster, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('class_id', 'day', 'period_no')
    
    def __str__(self):
        return f"Class {self.class_id} - {self.day} - Period {self.period_no}"