from django.contrib import admin
from .models import LessonPackage

@admin.register(LessonPackage)
class LessonPackageAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_hours', 'used_hours', 'remaining_hours_display')

    def remaining_hours_display(self, obj):
        return obj.remaining_hours
    remaining_hours_display.short_description = "Heures restantes"
