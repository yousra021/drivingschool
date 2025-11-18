from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, ListView
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from planning.models import LessonPackage, Appointment
from accounts.models import User

@login_required
def dashboard_view(request):
    role = request.user.role

    if role == "STUDENT":
        return redirect('student_dashboard')
    elif role == "INSTRUCTOR":
        return redirect('instructor_dashboard')
    elif role == "SECRETARY":
        return redirect('secretary_dashboard')
    elif role == "ADMIN":
        return redirect('admin_dashboard')
    else:
        return HttpResponseForbidden("Rôle inconnu")


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/student_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "STUDENT":
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            package = self.request.user.lessonpackage
            context["remaining_hours"] = package.remaining_hours
        except LessonPackage.DoesNotExist:
            context["remaining_hours"] = 0
        return context


class InstructorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/instructor_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == "INSTRUCTOR":
            students = User.objects.filter(role="STUDENT", instructor=self.request.user)
            context["students"] = students
        else:
            context["students"] = []
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "INSTRUCTOR":
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)


class SecretaryDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/secretary_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "SECRETARY":
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)
    
class StudentDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "student"
    pk_url_kwarg = "student_id"

    def get_template_names(self):
        if self.request.user.role == "INSTRUCTOR":
            return ["dashboard/student_detail_instructor.html"]
        else:
            return ["dashboard/student_detail.html"]

    def get_queryset(self):
        if self.request.user.role == "INSTRUCTOR":
            return User.objects.filter(role="STUDENT", instructor=self.request.user)
        elif self.request.user.role in ["SECRETARY", "ADMIN"]:
            return User.objects.filter(role="STUDENT")
        else:
            return User.objects.none()

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["INSTRUCTOR", "SECRETARY", "ADMIN"]:
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()

        try:
            package = student.LessonPackage
            context["package"] = package
            context["remaining_hours"] = package.remaining_hours
        except LessonPackage.DoesNotExist:
            context["package"] = None
            context["remaining_hours"] = 0

        context["appointments"] = Appointment.objects.filter(student=student).order_by("date", "time")
        return context

class InstructorStudentListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "dashboard/instructor_student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        return User.objects.filter(role="STUDENT", instructor=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "INSTRUCTOR":
            return HttpResponseForbidden("Accès interdit")
        return super().dispatch(request, *args, **kwargs)
