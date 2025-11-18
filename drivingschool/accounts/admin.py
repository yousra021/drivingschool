from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rôle, Forfait & Instructeur', {'fields': ('role', 'remaining_hours', 'instructor')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Rôle, Forfait & Instructeur', {'fields': ('role', 'remaining_hours', 'instructor')}),
    )
    list_display = ('username', 'email', 'role', 'instructor', 'remaining_hours', 'is_staff')
    list_filter = ('role', 'instructor', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
