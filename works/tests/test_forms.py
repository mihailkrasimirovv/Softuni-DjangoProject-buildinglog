from django.test import TestCase

from common.tests.factories import days_from_today, make_activity, make_contractor, make_site
from works.forms import ActivityCreateForm, ActivityEditForm


def activity_form_data(site):
    return {
        "site": site.pk,
        "title": "Reinforced concrete slab",
        "stage": "3_structure",
        "start_date": days_from_today(-10),
        "end_date": days_from_today(20),
        "contractors": [],
        "description": "",
    }


class ActivityFormTests(TestCase):
    def setUp(self):
        self.site = make_site()

    def test_valid_form_with_contractor(self):
        contractor = make_contractor()
        data = activity_form_data(self.site)
        data["contractors"] = [contractor.pk]
        form = ActivityCreateForm(data)

        self.assertTrue(form.is_valid())
        activity = form.save()
        self.assertEqual(activity.progress, 0)
        self.assertEqual(activity.contractors.count(), 1)

    def test_create_form_has_no_progress_field(self):
        form = ActivityCreateForm()

        self.assertNotIn("progress", form.fields)

    def test_end_date_before_start_date(self):
        data = activity_form_data(self.site)
        data["end_date"] = days_from_today(-11)
        form = ActivityCreateForm(data)

        self.assertEqual(form.errors["end_date"], ["The end date cannot be before the start date."])

    def test_activity_cannot_start_before_the_site(self):
        data = activity_form_data(self.site)
        data["start_date"] = days_from_today(-200)
        form = ActivityCreateForm(data)

        self.assertIn("start_date", form.errors)

    def test_inactive_contractor_cannot_be_assigned(self):
        inactive = make_contractor(is_active=False)
        data = activity_form_data(self.site)
        data["contractors"] = [inactive.pk]
        form = ActivityCreateForm(data)

        self.assertIn("contractors", form.errors)

    def test_progress_cannot_be_more_than_100(self):
        activity = make_activity(self.site)
        data = activity_form_data(self.site)
        data["progress"] = 120
        form = ActivityEditForm(data, instance=activity)

        self.assertEqual(form.errors["progress"], ["Progress cannot be more than 100%."])

    def test_activity_in_the_future_cannot_have_progress(self):
        activity = make_activity(self.site)
        data = activity_form_data(self.site)
        data["start_date"] = days_from_today(5)
        data["end_date"] = days_from_today(9)
        data["progress"] = 10
        form = ActivityEditForm(data, instance=activity)

        self.assertIn("progress", form.errors)
