from django.urls import path
from . import views

urlpatterns = [
    path('purchase/', views.purchase_lesson, name='purchase_lesson'),
    path('purchase/success/', views.purchase_success, name='purchase_success'),
    path('purchase/cancel/', views.purchase_cancel, name='purchase_cancel'),
]
