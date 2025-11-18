from django.urls import path
from django.contrib.auth import views as auth_views
from .views import redirect_by_role, add_hours_to_student, add_hours, StudentCreateView, UserUpdateView, UserDeleteView, InstructorCreateView, StudentListView, StudentDetailView
from accounts.views import InstructorCreateView
from .views import logout_view

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("redirect-by-role/", redirect_by_role, name="redirect_by_role"),
    path('add-hours/', add_hours, name='add_hours'),
    path('add-hours/<int:student_id>/', add_hours_to_student, name='add_hours_to_student'),
    path('create-student/', StudentCreateView.as_view(), name='create_student'),
    path('edit-user/<int:pk>/', UserUpdateView.as_view(), name='edit_user'),
    path('delete-user/<int:pk>/', UserDeleteView.as_view(), name='delete_user'),
    path('create-instructor/', InstructorCreateView.as_view(), name='create_instructor'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('student/<int:student_id>/', StudentDetailView.as_view(), name='student_detail'),
    path('accounts/logout/', logout_view, name='logout'),
]



