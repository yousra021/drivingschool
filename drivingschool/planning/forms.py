from django import forms
from .models import Appointment
from accounts.models import User
from django.forms.widgets import DateInput, TimeInput
from django.utils.timezone import make_aware, now as timezone_now
from planning.models import LessonPackage

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['student', 'instructor', 'date', 'time', 'location']
        widgets = {
            'date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instructor = kwargs.pop('instructor', None)
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role='STUDENT')
        self.fields['date'].input_formats = ['%Y-%m-%d']
        self.fields['time'].input_formats = ['%H:%M']
        self.fields['instructor'].queryset = User.objects.filter(role='INSTRUCTOR')


    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        student = cleaned_data.get('student')

        if date and time:
            from datetime import datetime

            appointment_datetime = datetime.combine(date, time)
            aware_appointment = make_aware(appointment_datetime)

            if aware_appointment < timezone_now():
                raise forms.ValidationError("Vous ne pouvez pas créer un rendez-vous dans le passé.")

            if student:
                try:
                    package = student.lessonpackage
                except LessonPackage.DoesNotExist:
                    raise forms.ValidationError("L'étudiant ne possède pas de forfait d'heures.")

                if package.remaining_hours < 1:
                    raise forms.ValidationError("L'étudiant ne dispose pas d'assez d'heures pour prendre un rendez-vous.")

class LessonPurchaseForm(forms.Form):
    HOURS_CHOICES = [(i, f"{i} heure(s)") for i in range(1, 11)]
    hours = forms.ChoiceField(choices=HOURS_CHOICES, label="Nombre d’heures", widget=forms.Select(attrs={"class": "form-control"}))
