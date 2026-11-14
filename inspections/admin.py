from django.contrib import admin

from inspections.models import Inspection


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("title", "activity", "severity", "inspected_on", "due_date", "is_resolved")
    list_filter = ("severity", "is_resolved")
    search_fields = ("title", "inspector", "activity__title")
