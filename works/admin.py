from django.contrib import admin

from works.models import WorkActivity


@admin.register(WorkActivity)
class WorkActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "site", "stage", "start_date", "end_date", "progress")
    list_filter = ("stage", "site")
    search_fields = ("title", "site__name")
    filter_horizontal = ("contractors",)
