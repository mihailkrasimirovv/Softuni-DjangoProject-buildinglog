from django import forms

from common.forms import BootstrapFormMixin, ReadOnlyFieldsMixin
from contractors.models import Contractor, Trade


class ContractorBaseForm(BootstrapFormMixin, forms.ModelForm):
    """Fields, texts and validation shared by the create and edit forms."""

    class Meta:
        model = Contractor
        fields = [
            "company_name",
            "eik",
            "trade",
            "contact_person",
            "phone",
            "email",
            "is_active",
            "notes",
        ]
        labels = {
            "trade": "Main trade",
            "email": "E-mail",
        }
        help_texts = {
            "eik": "Unified Identification Code - 9 digits (13 for a branch).",
            "phone": "Digits only, for example +359888123456.",
        }
        widgets = {
            "company_name": forms.TextInput(attrs={"placeholder": "e.g. Balkan Stroy Ltd."}),
            "eik": forms.TextInput(attrs={"placeholder": "e.g. 203456789", "inputmode": "numeric"}),
            "contact_person": forms.TextInput(attrs={"placeholder": "e.g. Ivan Petrov"}),
            "phone": forms.TextInput(attrs={"placeholder": "+359888123456"}),
            "email": forms.EmailInput(attrs={"placeholder": "office@example.com (optional)"}),
            "notes": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Licences, equipment, remarks (optional)"}
            ),
        }
        error_messages = {
            "company_name": {"required": "Please enter the company name."},
            "eik": {"required": "Please enter the company EIK."},
            "trade": {"required": "Please choose the main trade of the company."},
            "contact_person": {"required": "Please enter a contact person."},
            "phone": {"required": "Please enter a phone number."},
            "email": {"invalid": "Enter a valid e-mail address, for example office@example.com."},
        }

    def clean_company_name(self):
        return " ".join(self.cleaned_data["company_name"].split())

    def clean_contact_person(self):
        return " ".join(self.cleaned_data["contact_person"].split())

    def clean_phone(self):
        return self.cleaned_data["phone"].replace(" ", "")

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class ContractorCreateForm(ContractorBaseForm):
    pass


class ContractorEditForm(ReadOnlyFieldsMixin, ContractorBaseForm):
    """The EIK is the legal identity of the company, so it cannot be changed."""

    read_only_fields = ["eik"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["eik"].help_text = "The EIK cannot be changed after registration."

    def clean_is_active(self):
        is_active = self.cleaned_data["is_active"]
        has_unfinished_work = self.instance.activities.filter(progress__lt=100).exists()
        if not is_active and has_unfinished_work:
            raise forms.ValidationError(
                "This contractor is still assigned to unfinished activities "
                "and cannot be deactivated."
            )
        return is_active


class ContractorDeleteForm(ReadOnlyFieldsMixin, BootstrapFormMixin, forms.ModelForm):
    """Shown on the delete confirmation page. All fields are disabled."""

    read_only_fields = ["company_name", "eik", "trade", "contact_person"]

    class Meta:
        model = Contractor
        fields = ["company_name", "eik", "trade", "contact_person"]
        labels = {"trade": "Main trade"}


class ContractorFilterForm(BootstrapFormMixin, forms.Form):
    """Search and filter fields above the list of contractors."""

    TRADE_CHOICES = [("", "All trades")] + Trade.choices
    AVAILABILITY_CHOICES = [
        ("", "Active and inactive"),
        ("active", "Active only"),
        ("inactive", "Inactive only"),
    ]

    q = forms.CharField(
        required=False,
        max_length=60,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Company, EIK or contact person"}),
    )
    trade = forms.ChoiceField(
        required=False,
        choices=TRADE_CHOICES,
        error_messages={"invalid_choice": "Choose a trade from the list."},
    )
    activity = forms.ChoiceField(
        required=False,
        label="Availability",
        choices=AVAILABILITY_CHOICES,
        error_messages={"invalid_choice": "Choose an option from the list."},
    )
