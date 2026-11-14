from django.core.exceptions import ValidationError
from django.test import TestCase

from common.tests.factories import days_from_today, make_activity, make_site


class ConstructionSiteModelTests(TestCase):
    def test_str_is_the_name(self):
        site = make_site(name="Vitosha Park Residence")

        self.assertEqual(str(site), "Vitosha Park Residence")

    def test_wrong_permit_number_is_not_valid(self):
        site = make_site()
        site.permit_number = "145-2026"

        with self.assertRaises(ValidationError):
            site.full_clean()

    def test_completion_must_be_after_the_start(self):
        site = make_site()
        site.planned_end_date = site.start_date

        with self.assertRaises(ValidationError):
            site.full_clean()

    def test_progress_is_the_average_of_the_activities(self):
        site = make_site()
        self.assertEqual(site.progress, 0)

        make_activity(site, title="First", progress=100)
        make_activity(site, title="Second", progress=50)

        self.assertEqual(site.progress, 75)

    def test_is_overdue(self):
        site = make_site()
        self.assertFalse(site.is_overdue)

        site.planned_end_date = days_from_today(-1)
        self.assertTrue(site.is_overdue)

        site.status = "completed"
        self.assertFalse(site.is_overdue)
