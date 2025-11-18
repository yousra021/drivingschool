from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Appointment
from .forms import AppointmentForm
from planning.models import LessonPackage
from accounts.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import LessonPurchase
from .forms import LessonPurchaseForm
import stripe
from django.conf import settings

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'planning/create_appointment.html'
    success_url = reverse_lazy('secretary_dashboard')

    def form_valid(self, form):
        user = self.request.user

        if user.role == 'INSTRUCTOR':
            form.instance.instructor = user

        student = form.instance.student

        try:
            package = LessonPackage.objects.get(student=student)
        except LessonPackage.DoesNotExist:
            messages.error(self.request, "Erreur : Cet étudiant n'a pas de forfait d'heures.")
            return self.form_invalid(form)

        if package.remaining_hours <= 0:
            messages.error(self.request, "Erreur : Cet étudiant n'a plus d'heures disponibles.")
            return self.form_invalid(form)

        package.used_hours += 1
        package.save()

        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.role == 'INSTRUCTOR':
            return reverse_lazy('user_planning')
        return reverse_lazy('secretary_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['INSTRUCTOR', 'SECRETARY']:
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'planning/appointment_update.html'
    success_url = reverse_lazy('secretary_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['INSTRUCTOR', 'SECRETARY']:
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.user.role == 'INSTRUCTOR':
            return reverse_lazy('user_planning')
        return reverse_lazy('secretary_dashboard')


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'planning/confirm_delete.html'
    success_url = reverse_lazy('secretary_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['INSTRUCTOR', 'SECRETARY']:
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.user.role == 'INSTRUCTOR':
            return reverse_lazy('user_planning')
        return reverse_lazy('secretary_dashboard')


@login_required
def user_planning(request):
    user = request.user

    if user.role == "STUDENT":
        appointments = Appointment.objects.filter(student=user).order_by('date', 'time')
        try:
            package = LessonPackage.objects.get(student=user)
            total_hours = package.total_hours
            remaining_hours = package.remaining_hours
            used_hours = total_hours - remaining_hours
        except LessonPackage.DoesNotExist:
            total_hours = 0
            remaining_hours = 0
            used_hours = 0
    elif user.role == "INSTRUCTOR":
        appointments = Appointment.objects.filter(instructor=user).order_by('date', 'time')
        total_hours = None
        remaining_hours = None
        used_hours = None
    else:
        appointments = []
        total_hours = None
        remaining_hours = None
        used_hours = None

    return render(request, "planning/planning.html", {
        "appointments": appointments,
        "total_hours": total_hours,
        "remaining_hours": remaining_hours,
        "used_hours": used_hours,
    })


def is_secretary(user):
    return user.role == 'SECRETARY'


@login_required
def planning_list(request):
    if request.user.role != 'SECRETARY':
        return HttpResponseForbidden("Accès réservé")

    instructor_id = request.GET.get('instructor')

    appointments = Appointment.objects.all().order_by('date', 'time')
    instructors = User.objects.filter(role='INSTRUCTOR')

    if instructor_id:
        appointments = appointments.filter(instructor_id=instructor_id)

    return render(request, 'planning/planning_list.html', {
        'appointments': appointments,
        'instructors': instructors,
        'selected_instructor_id': int(instructor_id) if instructor_id else None
    })


@login_required
def user_planning_detail(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if target_user.role == 'STUDENT':
        appointments = Appointment.objects.filter(student=target_user).order_by('date', 'time')
        try:
            package = LessonPackage.objects.get(student=target_user)
            remaining_hours = package.remaining_hours
        except LessonPackage.DoesNotExist:
            remaining_hours = None
    elif target_user.role == 'INSTRUCTOR':
        appointments = Appointment.objects.filter(instructor=target_user).order_by('date', 'time')
        remaining_hours = None
    else:
        return HttpResponseForbidden("Cet utilisateur n'est ni élève ni moniteur.")

    return render(request, 'planning/user_planning_detail.html', {
        'target_user': target_user,
        'appointments': appointments,
        'remaining_hours': remaining_hours
    })




stripe.api_key = "sk_test_..." 

@login_required
def purchase_lesson(request):
    if request.user.role != 'STUDENT':
        return HttpResponseForbidden("Accès réservé aux élèves.")

    if request.method == 'POST':
        form = LessonPurchaseForm(request.POST)
        if form.is_valid():
            hours = int(form.cleaned_data['hours'])
            amount = hours * 30 

            purchase = LessonPurchase.objects.create(
                student=request.user,
                hours_purchased=hours,
                amount_paid=amount,
                payment_status='PENDING'
            )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f'{hours} heure(s) de conduite',
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/purchase/success/') + f"?purchase_id={purchase.id}",
                cancel_url=request.build_absolute_uri('/purchase/cancel/'),
            )
            return redirect(checkout_session.url, code=303)
    else:
        form = LessonPurchaseForm()

    return render(request, 'planning/purchase_lesson.html', {'form': form})


@login_required
def purchase_success(request):
    purchase_id = request.GET.get("purchase_id")
    if purchase_id:
        try:
            purchase = LessonPurchase.objects.get(id=purchase_id, student=request.user)
            purchase.payment_status = 'PAID'
            purchase.save()

            from .models import LessonPackage
            package, _ = LessonPackage.objects.get_or_create(student=request.user)
            package.total_hours += purchase.hours_purchased
            package.remaining_hours += purchase.hours_purchased
            package.save()
        except LessonPurchase.DoesNotExist:
            pass
    return render(request, 'planning/success.html')


@login_required
def purchase_cancel(request):
    return render(request, 'planning/cancel.html')
