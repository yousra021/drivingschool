from django.db import models
from accounts.models import User
from django.core.exceptions import ValidationError

class Appointment(models.Model):
    student = models.ForeignKey(User, related_name="appointments_as_student", on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    instructor = models.ForeignKey(User, related_name="appointments_as_instructor", on_delete=models.CASCADE, limit_choices_to={'role': 'INSTRUCTOR'})
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Rdv le {self.date} à {self.time} – Élève : {self.student.get_full_name()} / Moniteur : {self.instructor.get_full_name()}"

    def save(self, *args, **kwargs):
        try:
            package = self.student.lessonpackage
        except LessonPackage.DoesNotExist:
            raise ValidationError("L'élève ne possède pas de forfait d'heures.")

        if package.remaining_hours < 1:
            raise ValidationError("L'élève n'a plus d'heures disponibles.")

        package.used_hours += 1
        package.save()
        super().save(*args, **kwargs)


class LessonPackage(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    total_hours = models.PositiveIntegerField(default=0)
    used_hours = models.PositiveIntegerField(default=0)

    @property
    def remaining_hours(self):
        return self.total_hours - self.used_hours

    def __str__(self):
        return f"{self.student.username} - {self.remaining_hours}h restantes"
    
    
class LessonPurchase(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    hours_purchased = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('PENDING', 'En attente'), ('PAID', 'Payé')])
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.hours_purchased}h - {self.amount_paid}€"
