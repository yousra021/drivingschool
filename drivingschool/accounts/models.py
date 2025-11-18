from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT'
        INSTRUCTOR = 'INSTRUCTOR'
        SECRETARY = 'SECRETARY'
        ADMIN = 'ADMIN'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    remaining_hours = models.IntegerField(default=0)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "INSTRUCTOR"},
        related_name="students_assigned"
    )

class StudentInstructorRelation(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_instructor',
        limit_choices_to={'role': 'STUDENT'}
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_students',
        limit_choices_to={'role': 'INSTRUCTOR'}
    )

    def __str__(self):
        return f"{self.student.username} → {self.instructor.username}"
