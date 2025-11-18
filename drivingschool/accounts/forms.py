from django import forms
from accounts.models import User
from django.contrib.auth.forms import UserCreationForm
from planning.models import LessonPackage

class AssignInstructorForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['instructor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor'].queryset = User.objects.filter(role='INSTRUCTOR')
        self.fields['instructor'].label = "Choisir un instructeur"

class AddLessonHoursForm(forms.Form):
    student = forms.ModelChoiceField(queryset=User.objects.filter(role='STUDENT'), required=False)
    hours = forms.IntegerField(min_value=1, label="Nombre d'heures à ajouter")

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._student = student 
        if student:
            self.fields.pop('student')

    def apply(self):
        student = self._student or self.cleaned_data['student']
        hours = self.cleaned_data['hours']
        
        if student: 
            package, created = LessonPackage.objects.get_or_create(student=student)
            package.total_hours += hours
            package.save()
        
class CreateStudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'STUDENT'
        if commit:
            user.save()
        return user
    
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
