from django import template
from django.utils import timezone

register = template.Library()

BADGE_CLASSES = {
    # construction site status
    "planned": "text-bg-secondary",
    "active": "text-bg-primary",
    "on_hold": "text-bg-warning",
    "completed": "text-bg-success",
    # work activity state
    "upcoming": "text-bg-secondary",
    "in_progress": "text-bg-primary",
    "delayed": "text-bg-danger",
    # inspection severity
    "low": "text-bg-info",
    "medium": "text-bg-warning",
    "high": "badge-high",
    "critical": "text-bg-danger",
}


@register.filter
def badge_class(value):
    """Bootstrap badge class for a status, state or severity."""
    return BADGE_CLASSES.get(str(value), "text-bg-light")


@register.filter
def deadline_label(value):
    """Text like "5 days left", "due today" or "2 days overdue" for a date."""
    if not value:
        return ""
    days = (value - timezone.localdate()).days
    if days == 0:
        return "due today"
    if days == 1:
        return "1 day left"
    if days == -1:
        return "1 day overdue"
    if days > 0:
        return f"{days} days left"
    return f"{-days} days overdue"


@register.inclusion_tag("partials/progress_bar.html")
def progress_bar(value, show_label=True):
    """Bootstrap progress bar for a value between 0 and 100."""
    if value is None:
        value = 0
    percent = round(value)
    if percent == 100:
        colour = "bg-success"
    elif percent >= 50:
        colour = "bg-primary"
    else:
        colour = "bg-warning"
    return {"percent": percent, "colour": colour, "show_label": show_label}
