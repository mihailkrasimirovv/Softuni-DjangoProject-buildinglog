from django.contrib import admin

from contractors.models import Contractor


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("company_name", "eik", "trade", "contact_person", "is_active")
    list_filter = ("trade", "is_active")
    search_fields = ("company_name", "eik", "contact_person")
