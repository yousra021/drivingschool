from django import forms

class LessonPurchaseForm(forms.Form):
    HOURS_CHOICES = [(i, f"{i} heure(s)") for i in range(1, 11)]
    hours = forms.ChoiceField(
        choices=HOURS_CHOICES,
        label="Nombre d’heures",
        widget=forms.Select(attrs={"class": "form-control"})
    )
