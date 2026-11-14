from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.urls import reverse

from common.models import TimeStampedModel
from common.validators import validate_person_name, validate_phone_number


class Trade(models.TextChoices):
    EARTHWORKS = "earthworks", "Earthworks"
    CONCRETE = "concrete", "Concrete & formwork"
    MASONRY = "masonry", "Masonry"
    STEEL = "steel", "Steel structures"
    ROOFING = "roofing", "Roofing & waterproofing"
    ELECTRICAL = "electrical", "Electrical installations"
    PLUMBING = "plumbing", "Water supply & sewerage"
    HVAC = "hvac", "Heating, ventilation & air conditioning"
    FINISHING = "finishing", "Finishing works"
    SURVEYING = "surveying", "Geodesy & surveying"


class Contractor(TimeStampedModel):
    """A company hired to carry out a specific trade on the sites."""

    Trade = Trade

    company_name = models.CharField(
        max_length=120,
        unique=True,
        validators=[MinLengthValidator(2, "The company name must be at least 2 characters long.")],
        error_messages={"unique": "A contractor with this company name already exists."},
    )
    eik = models.CharField(
        "company ID (EIK)",
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(r"^(\d{9}|\d{13})$", "The EIK must contain exactly 9 or 13 digits.")
        ],
        error_messages={"unique": "A contractor with this EIK is already registered."},
    )
    trade = models.CharField(max_length=20, choices=Trade.choices)
    contact_person = models.CharField(max_length=80, validators=[validate_person_name])
    phone = models.CharField(max_length=16, validators=[validate_phone_number])
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Only active contractors can be assigned to new work activities.",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("contractors:detail", kwargs={"pk": self.pk})

    @property
    def activity_count(self):
        return self.activities.count()
