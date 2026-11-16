from django import forms
from django.utils import timezone

from common.forms import BootstrapFormMixin, DateInput, ReadOnlyFieldsMixin
from inspections.models import Inspection, Severity
from sites.models import ConstructionSite
from works.models import WorkActivity


class ActivityChoiceField(forms.ModelChoiceField):
    """Show the site in front of the activity title in the list of choices."""

    def label_from_instance(self, activity):
        return f"{activity.site.name} - {activity.title}"


class InspectionBaseForm(BootstrapFormMixin, forms.ModelForm):
    """Fields, texts and validation shared by the create and edit forms."""

    activity = ActivityChoiceField(
        queryset=WorkActivity.objects.select_related("site").order_by("site__name", "title"),
        empty_label="Choose an activity",
        label="Inspected activity",
        error_messages={
            "required": "Please choose the inspected activity.",
            "invalid_choice": "Choose an activity from the list.",
        },
    )

    class Meta:
        model = Inspection
        # The resolution fields are filled in later through the resolve form.
        fields = [
            "activity",
            "title",
            "inspector",
            "inspected_on",
            "severity",
            "finding",
            "due_date",
        ]
        labels = {
            "title": "Short title",
            "inspector": "Inspector",
            "finding": "Finding",
        }
        help_texts = {
            "inspected_on": "Cannot be in the future or before the start of the activity.",
            "due_date": "Deadline for fixing the issue. Required for critical findings.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Missing rebar spacers in slab"}),
            "inspector": forms.TextInput(attrs={"placeholder": "e.g. eng. Maria Georgieva"}),
            "inspected_on": DateInput(),
            "due_date": DateInput(),
            "finding": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "What was found, where exactly and what has to be done",
                }
            ),
        }
        error_messages = {
            "title": {"required": "Please enter a short title for the finding."},
            "inspector": {"required": "Please enter the name of the inspector."},
            "inspected_on": {"required": "Please choose the inspection date."},
            "finding": {"required": "Please describe the finding."},
        }

    def clean_title(self):
        return " ".join(self.cleaned_data["title"].split())

    def clean_inspector(self):
        return " ".join(self.cleaned_data["inspector"].split())

    def clean_inspected_on(self):
        inspected_on = self.cleaned_data["inspected_on"]
        if inspected_on > timezone.localdate():
            raise forms.ValidationError("The inspection date cannot be in the future.")
        return inspected_on

    def clean(self):
        cleaned_data = super().clean()
        activity = cleaned_data.get("activity")
        inspected_on = cleaned_data.get("inspected_on")
        due_date = cleaned_data.get("due_date")
        severity = cleaned_data.get("severity")

        if activity and inspected_on:
            if inspected_on < activity.start_date:
                activity_start = activity.start_date.strftime("%d.%m.%Y")
                self.add_error(
                    "inspected_on",
                    f"The activity starts on {activity_start} and cannot be inspected earlier.",
                )
        if inspected_on and due_date and due_date < inspected_on:
            self.add_error("due_date", "The deadline cannot be before the inspection date.")
        if severity == Severity.CRITICAL and not due_date and "due_date" not in self.errors:
            self.add_error("due_date", "A critical finding must have a deadline.")
        return cleaned_data


class InspectionCreateForm(InspectionBaseForm):
    pass


class InspectionEditForm(ReadOnlyFieldsMixin, InspectionBaseForm):
    """A finding belongs to the activity it was recorded for."""

    read_only_fields = ["activity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["activity"].help_text = "The inspected activity cannot be changed."


class InspectionResolveForm(ReadOnlyFieldsMixin, BootstrapFormMixin, forms.ModelForm):
    """Close a finding: the finding itself is shown read-only."""

    read_only_fields = ["title", "severity", "inspected_on"]

    class Meta:
        model = Inspection
        fields = ["title", "severity", "inspected_on", "resolved_on", "resolution_note"]
        labels = {
            "title": "Finding",
            "resolution_note": "What was done",
        }
        help_texts = {
            "resolved_on": "Cannot be in the future or before the inspection date.",
        }
        widgets = {
            "inspected_on": DateInput(),
            "resolved_on": DateInput(),
            "resolution_note": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Describe how the issue was fixed"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resolved_on"].required = True
        self.fields["resolved_on"].error_messages["required"] = "Please choose the resolution date."
        self.fields["resolution_note"].required = True
        self.fields["resolution_note"].error_messages[
            "required"
        ] = "Please describe how the issue was fixed."
        if not self.is_bound and not self.instance.resolved_on:
            self.initial["resolved_on"] = timezone.localdate()

    def clean_resolved_on(self):
        resolved_on = self.cleaned_data["resolved_on"]
        if resolved_on > timezone.localdate():
            raise forms.ValidationError("The resolution date cannot be in the future.")
        if resolved_on < self.instance.inspected_on:
            raise forms.ValidationError("The resolution date cannot be before the inspection date.")
        return resolved_on

    def clean_resolution_note(self):
        note = self.cleaned_data["resolution_note"].strip()
        if len(note) < 10:
            raise forms.ValidationError("Describe the fix with at least 10 characters.")
        return note

    def save(self, commit=True):
        inspection = super().save(commit=False)
        inspection.resolve(self.cleaned_data["resolved_on"], self.cleaned_data["resolution_note"])
        if commit:
            inspection.save()
        return inspection


class InspectionDeleteForm(ReadOnlyFieldsMixin, BootstrapFormMixin, forms.ModelForm):
    """Shown on the delete confirmation page. All fields are disabled."""

    read_only_fields = ["title", "inspector", "inspected_on", "severity"]

    class Meta:
        model = Inspection
        fields = ["title", "inspector", "inspected_on", "severity"]
        labels = {"title": "Short title"}
        widgets = {"inspected_on": DateInput()}


class InspectionFilterForm(BootstrapFormMixin, forms.Form):
    """Filter and sort fields above the list of inspections."""

    SEVERITY_CHOICES = [("", "All severities")] + Severity.choices
    STATE_CHOICES = [
        ("", "Open and resolved"),
        ("open", "Open"),
        ("overdue", "Overdue"),
        ("resolved", "Resolved"),
    ]
    SORT_CHOICES = [
        ("", "Open first"),
        ("newest", "Newest first"),
        ("oldest", "Oldest first"),
    ]

    site = forms.ModelChoiceField(
        required=False,
        queryset=ConstructionSite.objects.all(),
        empty_label="All sites",
        error_messages={"invalid_choice": "Choose a site from the list."},
    )
    severity = forms.ChoiceField(
        required=False,
        choices=SEVERITY_CHOICES,
        error_messages={"invalid_choice": "Choose a severity from the list."},
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
