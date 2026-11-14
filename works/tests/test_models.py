from django.core.exceptions import ValidationError
from django.test import TestCase

from common.tests.factories import days_from_today, make_activity, make_contractor, make_site
from works.models import WorkActivity


class WorkActivityModelTests(TestCase):
    def setUp(self):
        self.site = make_site()

    def test_state_depends_on_dates_and_progress(self):
        activity = make_activity(self.site)
        self.assertEqual(activity.state, "in_progress")

        activity.end_date = days_from_today(-1)
        self.assertEqual(activity.state, "delayed")

        activity.progress = 100
        self.assertEqual(activity.state, "completed")

        activity.progress = 0
        activity.start_date = days_from_today(5)
        activity.end_date = days_from_today(9)
        self.assertEqual(activity.state, "upcoming")

    def test_title_is_unique_for_the_site(self):
        make_activity(self.site, title="Excavation")
        duplicate = WorkActivity(
            site=self.site,
            title="Excavation",
            stage="1_excavation",
            start_date=days_from_today(0),
            end_date=days_from_today(5),
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_progress_cannot_be_more_than_100(self):
        activity = make_activity(self.site)
        activity.progress = 101

        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_activity_can_have_many_contractors(self):
        activity = make_activity(self.site)
        first = make_contractor()
        second = make_contractor(company_name="Geo Point", eik="111222333")

        activity.contractors.add(first, second)

        self.assertEqual(activity.contractors.count(), 2)
        self.assertEqual(first.activities.count(), 1)

    def test_deleting_the_site_deletes_its_activities(self):
        make_activity(self.site)

        self.site.delete()

        self.assertEqual(WorkActivity.objects.count(), 0)
