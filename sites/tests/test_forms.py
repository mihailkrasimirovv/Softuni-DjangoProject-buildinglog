from django.test import TestCase

from common.tests.factories import days_from_today, make_activity, make_site
from sites.forms import SiteCreateForm, SiteEditForm


def site_form_data():
    return {
        "name": "Vitosha Park Residence",
        "permit_number": "RS-145/2026",
        "site_type": "residential",
        "status": "planned",
        "city": "Sofia",
        "address": "12 Vitosha Blvd",
        "investor": "Balkan Invest Ltd.",
        "gross_floor_area": "4250.50",
        "start_date": days_from_today(10),
        "planned_end_date": days_from_today(400),
        "description": "",
    }


class SiteFormTests(TestCase):
    def test_valid_form(self):
        data = site_form_data()
        data["permit_number"] = "rs-145/2026"
        form = SiteCreateForm(data)

        self.assertTrue(form.is_valid())
        site = form.save()
        self.assertEqual(site.permit_number, "RS-145/2026")

    def test_wrong_permit_number(self):
        data = site_form_data()
        data["permit_number"] = "145/2026"
        form = SiteCreateForm(data)

        self.assertIn("permit_number", form.errors)

    def test_duplicate_permit_number(self):
        make_site(permit_number="RS-145/2026")
        form = SiteCreateForm(site_form_data())

        self.assertEqual(
            form.errors["permit_number"], ["This construction permit is already registered."]
        )

    def test_end_date_must_be_after_start_date(self):
        data = site_form_data()
        data["planned_end_date"] = data["start_date"]
        form = SiteCreateForm(data)

        self.assertIn("planned_end_date", form.errors)

    def test_permit_number_cannot_be_changed_in_the_edit_form(self):
        site = make_site(permit_number="RS-7/2025")
        data = site_form_data()
        data["permit_number"] = "RS-999/2030"
        form = SiteEditForm(data, instance=site)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().permit_number, "RS-7/2025")

    def test_site_with_unfinished_activities_cannot_be_completed(self):
        site = make_site()
        make_activity(site, progress=80)
        data = site_form_data()
        data["status"] = "completed"
        form = SiteEditForm(data, instance=site)

        self.assertIn("status", form.errors)
