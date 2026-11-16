from django import forms
from django.utils import timezone

from common.forms import BootstrapFormMixin, DateInput, ReadOnlyFieldsMixin
from contractors.models import Contractor
from sites.models import ConstructionSite
from works.models import ActivityState, Stage, WorkActivity


class ContractorChoiceField(forms.ModelMultipleChoiceField):
    """Shows the trade next to the company name in the list of contractors."""

    def label_from_instance(self, contractor):
        return f"{contractor.company_name} ({contractor.get_trade_display()})"


class ActivityBaseForm(BootstrapFormMixin, forms.ModelForm):
    """Common part of the create and edit forms."""

    contractors = ContractorChoiceField(
        queryset=Contractor.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Assigned contractors",
        help_text="Only active contractors can be assigned.",
        error_messages={"invalid_choice": "One of the selected contractors is not available."},
    )

    class Meta:
        model = WorkActivity
        fields = ["site", "title", "stage", "start_date", "end_date", "contractors", "description"]
        labels = {
            "site": "Construction site",
            "stage": "Construction stage",
        }
        help_texts = {
            "title": "The title must be unique within the site.",
            "end_date": "Cannot be before the start date.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Reinforced concrete slab +3.00"}),
            "start_date": DateInput(),
            "end_date": DateInput(),
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Scope of the works, quantities (optional)"}
            ),
        }
        error_messages = {
            "site": {"required": "Please choose the construction site."},
            "title": {"required": "Please enter a title for the activity."},
            "stage": {"required": "Please choose the construction stage."},
            "start_date": {"required": "Please choose the start date."},
            "end_date": {"required": "Please choose the end date."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["site"].empty_label = "Choose a site"

    def clean_title(self):
        return " ".join(self.cleaned_data["title"].split())

    def clean(self):
        cleaned_data = super().clean()
        site = cleaned_data.get("site")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                self.add_error("end_date", "The end date cannot be before the start date.")

        if site and start_date:
            if start_date < site.start_date:
                site_start = site.start_date.strftime("%d.%m.%Y")
                self.add_error(
                    "start_date",
                    f"The activity cannot start before the site itself ({site_start}).",
                )
        return cleaned_data


class ActivityCreateForm(ActivityBaseForm):
    """A new activity always starts at 0%, so there is no progress field here."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["site"].queryset = ConstructionSite.objects.exclude(status="completed")
        self.fields["site"].help_text = "Completed sites are not listed."


class ActivityEditForm(ReadOnlyFieldsMixin, ActivityBaseForm):
    """The site cannot be changed. The progress is reported with this form."""

    read_only_fields = ["site"]

    class Meta(ActivityBaseForm.Meta):
        fields = [
            "site",
            "title",
            "stage",
            "start_date",
            "end_date",
            "contractors",
            "progress",
            "description",
        ]
        help_texts = {
            "site": "An activity cannot be moved to another site.",
            "title": "The title must be unique within the site.",
            "end_date": "Cannot be before the start date.",
            "progress": "Whole number between 0 and 100.",
        }
        error_messages = {
            "title": {"required": "Please enter a title for the activity."},
            "stage": {"required": "Please choose the construction stage."},
            "start_date": {"required": "Please choose the start date."},
            "end_date": {"required": "Please choose the end date."},
            "progress": {
                "required": "Please enter the current progress.",
                "invalid": "Progress must be a whole number between 0 and 100.",
                "min_value": "Progress cannot be negative.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["progress"].widget.attrs["placeholder"] = "0 - 100"
        # contractors that are already assigned stay in the list even if they are not active now
        active = Contractor.objects.filter(is_active=True)
        assigned = self.instance.contractors.all()
        self.fields["contractors"].queryset = (active | assigned).distinct()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        progress = cleaned_data.get("progress")
        if start_date and progress:
            if start_date > timezone.localdate():
                self.add_error(
                    "progress", "An activity that has not started yet cannot have progress."
                )
        return cleaned_data


class ActivityDeleteForm(ReadOnlyFieldsMixin, BootstrapFormMixin, forms.ModelForm):
    """Shown on the delete confirmation page. All fields are disabled."""

    read_only_fields = ["title", "site", "stage", "progress"]

    class Meta:
        model = WorkActivity
        fields = ["title", "site", "stage", "progress"]
        labels = {"site": "Construction site", "stage": "Construction stage"}


class ActivityFilterForm(BootstrapFormMixin, forms.Form):
    """Search, filter and sort fields above the list of activities."""

    STAGE_CHOICES = [("", "All stages")] + Stage.choices
    STATE_CHOICES = [("", "All states")] + ActivityState.choices
    SORT_CHOICES = [
        ("start", "Start date"),
        ("deadline", "End date"),
        ("stage", "Construction stage"),
        ("progress", "Least progress"),
    ]

    q = forms.CharField(
        required=False,
        max_length=60,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Activity title"}),
    )
    site = forms.ModelChoiceField(
        required=False,
        queryset=ConstructionSite.objects.all(),
        empty_label="All sites",
        error_messages={"invalid_choice": "Choose a site from the list."},
    )
    stage = forms.ChoiceField(
        required=False,
        choices=STAGE_CHOICES,
        error_messages={"invalid_choice": "Choose a stage from the list."},
    )
    state = forms.ChoiceField(
        required=False,
        choices=STATE_CHOICES,
        error_messages={"invalid_choice": "Choose a state from the list."},
    )
    sort = forms.ChoiceField(
        required=False,
        label="Sort by",
        choices=SORT_CHOICES,
        error_messages={"invalid_choice": "Choose a sort order from the list."},
    )
