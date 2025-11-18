from django.urls import path
from .views import (
    dashboard_view,
    StudentDashboardView,
    InstructorDashboardView,
    SecretaryDashboardView,
    AdminDashboardView,
    StudentDetailView,
    InstructorStudentListView
)

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/instructor/", InstructorDashboardView.as_view(), name="instructor_dashboard"),
    path("student/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("secretary/", SecretaryDashboardView.as_view(), name="secretary_dashboard"),
    path("admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("student/<int:student_id>/", StudentDetailView.as_view(), name="student_detail"),
    path("instructor/students/", InstructorStudentListView.as_view(), name="instructor_students"),
]
