"""Helper functions that create valid objects for the tests."""

import datetime

from django.utils import timezone

from contractors.models import Contractor
from inspections.models import Inspection
from sites.models import ConstructionSite
from works.models import WorkActivity


def days_from_today(days):
    return timezone.localdate() + datetime.timedelta(days=days)


def make_site(name="Residential building", permit_number="RS-1/2026", status="active"):
    return ConstructionSite.objects.create(
        name=name,
        permit_number=permit_number,
        site_type="residential",
        status=status,
        city="Sofia",
        address="12 Vitosha Blvd",
        investor="Balkan Invest Ltd.",
        gross_floor_area="4250.50",
        start_date=days_from_today(-60),
        planned_end_date=days_from_today(300),
    )


def make_contractor(company_name="Beton Pro Ltd.", eik="203456789", is_active=True):
    return Contractor.objects.create(
        company_name=company_name,
        eik=eik,
        trade="concrete",
        contact_person="Ivan Petrov",
        phone="+359888123456",
        is_active=is_active,
    )


def make_activity(site, title="Concrete slab", progress=40):
    return WorkActivity.objects.create(
        site=site,
        title=title,
        stage="3_structure",
        start_date=days_from_today(-30),
        end_date=days_from_today(30),
        progress=progress,
    )


def make_inspection(activity, title="Missing rebar spacers", severity="medium"):
    return Inspection.objects.create(
        activity=activity,
        title=title,
        inspector="Maria Georgieva",
        inspected_on=days_from_today(-5),
        severity=severity,
        finding="Spacers are missing under the bottom reinforcement.",
        due_date=days_from_today(10),
    )
