from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import AddLessonHoursForm, CreateStudentForm, CustomUserCreationForm, EditUserForm, CreateStudentForm, AssignInstructorForm
from accounts.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from planning.models import LessonPackage
from django.contrib.auth import logout

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CreateStudentForm
    template_name = 'accounts/create_student.html'
    success_url = reverse_lazy('student_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'SECRETARY':
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditUserForm
    template_name = 'accounts/edit_user.html'
    success_url = reverse_lazy('student_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'SECRETARY':
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'SECRETARY':
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

class InstructorCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/create_instructor.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        form.instance.role = 'INSTRUCTOR'
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'SECRETARY':
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

class StudentListView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'students'
    template_name = 'dashboard/student_list.html'

    def get_queryset(self):
        return User.objects.filter(role='STUDENT')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['SECRETARY', 'ADMIN']:
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        student_data = []
        for student in context['students']:
            package = getattr(student, 'lessonpackage', None)
            student_data.append({'student': student, 'package': package})
        context['students'] = student_data
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'dashboard/student_detail.html'
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'

    def get_template_names(self):
        if self.request.user.role == 'INSTRUCTOR':
            return ['dashboard/student_detail_instructor.html']
        return ['dashboard/student_detail.html']


    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['SECRETARY', 'ADMIN', 'INSTRUCTOR']:
            return HttpResponseForbidden("Accès refusé")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, student_id, *args, **kwargs):
        self.object = self.get_object()
        form = AssignInstructorForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            return redirect('student_detail', student_id=self.object.id)
        return self.render_to_response(self.get_context_data(form=form))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        form = kwargs.get('form') or AssignInstructorForm(instance=student)

        try:
            package = student.lessonpackage
            context['package'] = package
            context['remaining_hours'] = package.remaining_hours
        except LessonPackage.DoesNotExist:
            context['package'] = None
            context['remaining_hours'] = 0

        context['appointments'] = student.appointments_as_student.all().order_by('date', 'time')
        context['form'] = form
        return context

@login_required
def add_hours(request):
    if request.user.role not in ['SECRETARY', 'ADMIN']:
        return HttpResponseForbidden("Accès refusé")

    if request.method == 'POST':
        form = AddLessonHoursForm(request.POST)
        if form.is_valid():
            form.apply()
            return redirect('student_list')
    else:
        form = AddLessonHoursForm()

    return render(request, 'accounts/add_hours.html', {'form': form})

@login_required
def redirect_by_role(request):
    role = request.user.role
    return redirect("dashboard")

@login_required
def add_hours_to_student(request, student_id):
    if request.user.role not in ['SECRETARY', 'ADMIN']:
        return HttpResponseForbidden("Accès réservé")

    student = get_object_or_404(User, id=student_id, role='STUDENT')

    if request.method == 'POST':
        form = AddLessonHoursForm(request.POST, student=student)
        if form.is_valid():
            form.apply()  
            return redirect('student_list')
    else:
        form = AddLessonHoursForm(student=student)

    return render(request, 'accounts/add_hours_to_student.html', {
        'form': form,
        'student': student
    })

    
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'accounts/logout.html')

def home(request):
    """Vue d'accueil qui redirige vers login ou dashboard selon l'état de connexion"""
    if request.user.is_authenticated:
        return redirect('redirect_by_role')
    return redirect('login')
