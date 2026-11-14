from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Avg, F, Q
from django.urls import reverse
from django.utils import timezone

from common.models import TimeStampedModel


class SiteType(models.TextChoices):
    RESIDENTIAL = "residential", "Residential building"
    COMMERCIAL = "commercial", "Commercial / office building"
    INDUSTRIAL = "industrial", "Industrial facility"
    INFRASTRUCTURE = "infrastructure", "Infrastructure"


class SiteStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    ACTIVE = "active", "Under construction"
    ON_HOLD = "on_hold", "On hold"
    COMPLETED = "completed", "Completed"


class ConstructionSite(TimeStampedModel):
    """A building site identified by its construction permit."""

    SiteType = SiteType
    Status = SiteStatus

    name = models.CharField(
        max_length=120,
        unique=True,
        validators=[MinLengthValidator(3, "The site name must be at least 3 characters long.")],
        error_messages={"unique": "A construction site with this name already exists."},
    )
    permit_number = models.CharField(
        "construction permit No.",
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                r"^RS-\d{1,5}/\d{4}$",
                "Use the format RS-<number>/<year>, for example RS-145/2026.",
            )
        ],
        error_messages={"unique": "This construction permit is already registered."},
    )
    site_type = models.CharField(
        "type", max_length=20, choices=SiteType.choices, default=SiteType.RESIDENTIAL
    )
    status = models.CharField(max_length=20, choices=SiteStatus.choices, default=SiteStatus.PLANNED)
    city = models.CharField(max_length=60)
    address = models.CharField(max_length=200)
    investor = models.CharField(max_length=120)
    gross_floor_area = models.DecimalField(
        "gross floor area (m²)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1, "The gross floor area must be at least 1 m².")],
    )
    start_date = models.DateField()
    planned_end_date = models.DateField("planned completion")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["planned_end_date", "name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(planned_end_date__gt=F("start_date")),
                name="site_end_after_start",
                violation_error_message="The planned completion must be after the start date.",
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("sites:detail", kwargs={"pk": self.pk})

    @property
    def activity_count(self):
        return self.activities.count()

    @property
    def progress(self):
        """Average progress of the activities of the site, in percent."""
        average = self.activities.aggregate(Avg("progress"))["progress__avg"]
        if average is None:
            return 0
        return round(average)

    @property
    def is_completed(self):
        return self.status == SiteStatus.COMPLETED

    @property
    def is_overdue(self):
        return not self.is_completed and self.planned_end_date < timezone.localdate()

    @property
    def duration_days(self):
        return (self.planned_end_date - self.start_date).days
