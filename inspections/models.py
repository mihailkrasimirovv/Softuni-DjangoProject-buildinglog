from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from common.models import TimeStampedModel
from common.validators import validate_person_name


class Severity(models.TextChoices):
    LOW = "low", "Minor"
    MEDIUM = "medium", "Moderate"
    HIGH = "high", "Major"
    CRITICAL = "critical", "Critical"


class Inspection(TimeStampedModel):
    """A finding recorded during a site inspection of a work activity."""

    Severity = Severity

    activity = models.ForeignKey(
        "works.WorkActivity", on_delete=models.PROTECT, related_name="inspections"
    )
    title = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(5, "The title must be at least 5 characters long.")],
    )
    inspector = models.CharField(max_length=80, validators=[validate_person_name])
    inspected_on = models.DateField("inspection date")
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    finding = models.TextField(
        validators=[MinLengthValidator(10, "Describe the finding with at least 10 characters.")]
    )
    due_date = models.DateField("fix by", null=True, blank=True)
    is_resolved = models.BooleanField("resolved", default=False)
    resolved_on = models.DateField("resolution date", null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    class Meta:
        ordering = ["is_resolved", "-inspected_on", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(due_date__isnull=True) | Q(due_date__gte=F("inspected_on")),
                name="inspection_due_not_before_inspected",
                violation_error_message="The deadline cannot be before the inspection date.",
            ),
            models.CheckConstraint(
                condition=Q(is_resolved=False) | Q(resolved_on__isnull=False),
                name="inspection_resolved_has_date",
                violation_error_message="A resolved inspection must have a resolution date.",
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("inspections:detail", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()
        if self.resolved_on and self.inspected_on and self.resolved_on < self.inspected_on:
            raise ValidationError("The resolution date cannot be before the inspection date.")

    @property
    def is_overdue(self):
        return (
            not self.is_resolved
            and self.due_date is not None
            and self.due_date < timezone.localdate()
        )

    def resolve(self, resolved_on, note):
        """Mark the finding as fixed."""
        self.is_resolved = True
        self.resolved_on = resolved_on
        self.resolution_note = note

    def reopen(self):
        """Put a resolved finding back in the open list."""
        self.is_resolved = False
        self.resolved_on = None
        self.resolution_note = ""
