import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from sites.models import ConstructionSite


def site_report_csv(request, site_pk):
    """Downloads the activities of one site as a CSV file (it can be opened in Excel)."""
    site = get_object_or_404(ConstructionSite, pk=site_pk)
    activities = site.activities.order_by("stage", "start_date")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="site-{site.pk}-progress-report.csv"'
    # Excel needs this mark at the beginning of the file to read UTF-8 correctly
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(
        [
            "Stage",
            "Activity",
            "Start date",
            "End date",
            "Progress (%)",
            "State",
            "Contractors",
            "Open inspections",
        ]
    )

    for activity in activities:
        contractor_names = []
        for contractor in activity.contractors.all():
            contractor_names.append(contractor.company_name)

        open_inspections = activity.inspections.filter(is_resolved=False).count()

        writer.writerow(
            [
                activity.get_stage_display(),
                activity.title,
                activity.start_date,
                activity.end_date,
                activity.progress,
                activity.state.label,
                "; ".join(contractor_names),
                open_inspections,
            ]
        )

    return response
