from django.contrib import admin

from sites.models import ConstructionSite


@admin.register(ConstructionSite)
class ConstructionSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "permit_number", "city", "status", "start_date", "planned_end_date")
    list_filter = ("status", "site_type")
    search_fields = ("name", "permit_number", "city", "investor")
