from django import forms

from common.forms import BootstrapFormMixin, DateInput, ReadOnlyFieldsMixin
from sites.models import ConstructionSite, SiteStatus


class SiteBaseForm(BootstrapFormMixin, forms.ModelForm):
    """Fields, texts and validation shared by the create and edit forms."""

    class Meta:
        model = ConstructionSite
        fields = [
            "name",
            "permit_number",
            "site_type",
            "status",
            "city",
            "address",
            "investor",
            "gross_floor_area",
            "start_date",
            "planned_end_date",
            "description",
        ]
        labels = {
            "name": "Site name",
            "investor": "Investor / client",
        }
        help_texts = {
            "permit_number": "Format: RS-<number>/<year>, for example RS-145/2026.",
            "gross_floor_area": "Total built-up area of all floors, in square metres.",
            "planned_end_date": "Must be after the start date.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Vitosha Park Residence - Block A"}),
            "permit_number": forms.TextInput(attrs={"placeholder": "RS-145/2026"}),
            "city": forms.TextInput(attrs={"placeholder": "e.g. Sofia"}),
            "address": forms.TextInput(attrs={"placeholder": "Street, number, district"}),
            "investor": forms.TextInput(
                attrs={"placeholder": "Company or person financing the project"}
            ),
            "gross_floor_area": forms.NumberInput(
                attrs={"placeholder": "e.g. 4250.50", "step": "0.01"}
            ),
            "start_date": DateInput(),
            "planned_end_date": DateInput(),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Short description of the building (optional)"}
            ),
        }
        error_messages = {
            "name": {"required": "Please enter the name of the construction site."},
            "permit_number": {"required": "Please enter the construction permit number."},
            "gross_floor_area": {
                "required": "Please enter the gross floor area.",
                "invalid": "Enter the area as a number, for example 4250.50.",
            },
            "start_date": {"required": "Please choose the start date."},
            "planned_end_date": {"required": "Please choose the planned completion date."},
        }

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean_permit_number(self):
        return self.cleaned_data["permit_number"].strip().upper()

    def clean_city(self):
        city = " ".join(self.cleaned_data["city"].split())
        for character in city:
            if character.isdigit():
                raise forms.ValidationError("The city name cannot contain digits.")
        return city

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        planned_end_date = cleaned_data.get("planned_end_date")
        if start_date and planned_end_date and planned_end_date <= start_date:
            self.add_error(
                "planned_end_date", "The planned completion must be after the start date."
            )
        return cleaned_data


class SiteCreateForm(SiteBaseForm):
    def clean_status(self):
        status = self.cleaned_data["status"]
        if status == SiteStatus.COMPLETED:
            raise forms.ValidationError(
                "A new site cannot be registered as completed. Choose another status."
            )
        return status


class SiteEditForm(ReadOnlyFieldsMixin, SiteBaseForm):
    """The construction permit identifies the site, so it cannot be changed."""

    read_only_fields = ["permit_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permit_number"].help_text = (
            "The permit number cannot be changed after registration."
        )

    def clean_status(self):
        status = self.cleaned_data["status"]
        has_unfinished_work = self.instance.activities.filter(progress__lt=100).exists()
        if status == SiteStatus.COMPLETED and has_unfinished_work:
            raise forms.ValidationError(
                "The site cannot be completed while it has activities below 100% progress."
            )
        return status


class SiteDeleteForm(ReadOnlyFieldsMixin, BootstrapFormMixin, forms.ModelForm):
    """Shown on the delete confirmation page. All fields are disabled."""

    read_only_fields = ["name", "permit_number", "city", "investor", "status"]

    class Meta:
        model = ConstructionSite
        fields = ["name", "permit_number", "city", "investor", "status"]
        labels = {"name": "Site name", "investor": "Investor / client"}


class SiteFilterForm(BootstrapFormMixin, forms.Form):
    """Search, filter and sort fields above the list of sites."""

    STATUS_CHOICES = [("", "All statuses")] + SiteStatus.choices
    SORT_CHOICES = [
        ("deadline", "Nearest deadline"),
        ("name", "Name (A-Z)"),
        ("newest", "Recently started"),
    ]

    q = forms.CharField(
        required=False,
        max_length=60,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Name, city or permit No."}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        error_messages={"invalid_choice": "Choose a status from the list."},
    )
    sort = forms.ChoiceField(
        required=False,
        label="Sort by",
        choices=SORT_CHOICES,
        error_messages={"invalid_choice": "Choose a sort order from the list."},
    )
