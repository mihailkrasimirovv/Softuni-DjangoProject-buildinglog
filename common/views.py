from django.db.models import Avg, Count
from django.utils import timezone
from django.views.generic import TemplateView

from contractors.models import Contractor
from inspections.models import Inspection
from sites.models import ConstructionSite
from works.models import WorkActivity


class HomeView(TemplateView):
    """Dashboard with the main numbers for all construction sites."""

    template_name = "common/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        unfinished_sites = ConstructionSite.objects.exclude(status="completed")
        open_inspections = Inspection.objects.filter(is_resolved=False)

        context["stats"] = {
            "sites_total": ConstructionSite.objects.count(),
            "sites_active": ConstructionSite.objects.filter(status="active").count(),
            "sites_overdue": unfinished_sites.filter(planned_end_date__lt=today).count(),
            "contractors_active": Contractor.objects.filter(is_active=True).count(),
            "activities_total": WorkActivity.objects.count(),
            "activities_delayed": WorkActivity.objects.filter(
                progress__lt=100, end_date__lt=today
            ).count(),
            "inspections_open": open_inspections.count(),
            "inspections_critical": open_inspections.filter(severity="critical").count(),
        }
        context["upcoming_sites"] = unfinished_sites.order_by("planned_end_date")[:4]
        context["latest_inspections"] = open_inspections.select_related("activity__site")[:5]

        # number of activities and average progress for every construction stage
        stage_rows = (
            WorkActivity.objects.values("stage")
            .annotate(total=Count("id"), average=Avg("progress"))
            .order_by("stage")
        )
        stage_labels = dict(WorkActivity.Stage.choices)
        stage_summary = []
        for row in stage_rows:
            stage_summary.append(
                {
                    "label": stage_labels[row["stage"]],
                    "total": row["total"],
                    "average": row["average"],
                }
            )
        context["stage_summary"] = stage_summary
        return context


class AboutView(TemplateView):
    template_name = "common/about.html"
