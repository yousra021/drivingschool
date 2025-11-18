from django.urls import path
from .views import user_planning, planning_list, user_planning_detail
from .views import (
    AppointmentCreateView,
    AppointmentUpdateView,
    AppointmentDeleteView,
)
from . import views

urlpatterns = [
    path("my-planning/", user_planning, name="user_planning"),
    path('', planning_list, name='planning_list'),
    path('user/<int:user_id>/', user_planning_detail, name='user_planning_detail'),
    path('appointment/create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointment/<int:pk>/update/', AppointmentUpdateView.as_view(), name='appointment_update'), 
    path('appointment/<int:pk>/delete/', AppointmentDeleteView.as_view(), name='appointment_delete'), 
    path('purchase/', views.purchase_lesson, name='purchase_lesson'),
    path('purchase/success/', views.purchase_success, name='purchase_success'),
    path('purchase/cancel/', views.purchase_cancel, name='purchase_cancel'),

]
