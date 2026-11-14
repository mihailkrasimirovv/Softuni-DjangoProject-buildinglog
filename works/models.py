from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from common.models import TimeStampedModel


class Stage(models.TextChoices):
    EXCAVATION = "1_excavation", "Excavation"
    FOUNDATIONS = "2_foundations", "Foundations"
    STRUCTURE = "3_structure", "Structure"
    ROOFING = "4_roofing", "Roofing"
    INSTALLATIONS = "5_installations", "Installations"
    FINISHING = "6_finishing", "Finishing works"
    LANDSCAPING = "7_landscaping", "Landscaping"


class ActivityState(models.TextChoices):
    """State of an activity, derived from its dates and progress."""

    UPCOMING = "upcoming", "Upcoming"
    IN_PROGRESS = "in_progress", "In progress"
    DELAYED = "delayed", "Delayed"
    COMPLETED = "completed", "Completed"


class WorkActivity(TimeStampedModel):
    """A package of construction works carried out on one site."""

    Stage = Stage
    State = ActivityState

    site = models.ForeignKey(
        "sites.ConstructionSite", on_delete=models.CASCADE, related_name="activities"
    )
    contractors = models.ManyToManyField(
        "contractors.Contractor", related_name="activities", blank=True
    )
    title = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(3, "The title must be at least 3 characters long.")],
    )
    stage = models.CharField(max_length=20, choices=Stage.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    progress = models.PositiveSmallIntegerField(
        "progress (%)",
        default=0,
        validators=[MaxValueValidator(100, "Progress cannot be more than 100%%.")],
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["start_date", "title"]
        verbose_name_plural = "work activities"
        constraints = [
            models.UniqueConstraint(
                fields=["site", "title"],
                name="unique_activity_title_per_site",
                violation_error_message="This site already has an activity with the same title.",
            ),
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="activity_end_not_before_start",
                violation_error_message="The end date cannot be before the start date.",
            ),
            models.CheckConstraint(
                condition=Q(progress__lte=100),
                name="activity_progress_max_100",
                violation_error_message="Progress cannot be more than 100%%.",
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("works:detail", kwargs={"pk": self.pk})

    @property
    def state(self):
        today = timezone.localdate()
        if self.progress >= 100:
            return ActivityState.COMPLETED
        if self.start_date > today:
            return ActivityState.UPCOMING
        if self.end_date < today:
            return ActivityState.DELAYED
        return ActivityState.IN_PROGRESS

    @property
    def is_completed(self):
        return self.state == ActivityState.COMPLETED

    @property
    def duration_days(self):
        """Number of calendar days, counting both the first and the last day."""
        return (self.end_date - self.start_date).days + 1
