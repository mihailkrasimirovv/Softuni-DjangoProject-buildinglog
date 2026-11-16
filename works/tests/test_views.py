from django.test import TestCase
from django.urls import reverse

from common.tests.factories import make_activity, make_inspection, make_site
from works.models import WorkActivity
from works.tests.test_forms import activity_form_data


class ActivityViewsTests(TestCase):
    def setUp(self):
        self.site = make_site()

    def test_list_filter_by_state(self):
        make_activity(self.site, title="Finished works", progress=100)
        make_activity(self.site, title="Running works", progress=40)

        response = self.client.get(reverse("works:list"), {"state": "completed"})

        self.assertContains(response, "Finished works")
        self.assertNotContains(response, "Running works")

    def test_create_page_selects_the_site_from_the_link(self):
        response = self.client.get(reverse("works:create"), {"site": self.site.pk})

        self.assertEqual(response.context["form"].initial["site"], self.site.pk)

    def test_create_activity(self):
        response = self.client.post(reverse("works:create"), activity_form_data(self.site))

        activity = WorkActivity.objects.get()
        self.assertRedirects(response, reverse("works:detail", kwargs={"pk": activity.pk}))

    def test_edit_activity_progress(self):
        activity = make_activity(self.site, progress=10)
        data = activity_form_data(self.site)
        data["progress"] = 75

        self.client.post(reverse("works:edit", kwargs={"pk": activity.pk}), data)

        activity.refresh_from_db()
        self.assertEqual(activity.progress, 75)

    def test_delete_activity_goes_back_to_the_site(self):
        activity = make_activity(self.site)

        response = self.client.post(reverse("works:delete", kwargs={"pk": activity.pk}))

        self.assertRedirects(response, reverse("sites:detail", kwargs={"pk": self.site.pk}))
        self.assertEqual(WorkActivity.objects.count(), 0)

    def test_activity_with_inspections_is_not_deleted(self):
        activity = make_activity(self.site)
        make_inspection(activity)

        response = self.client.post(reverse("works:delete", kwargs={"pk": activity.pk}))

        self.assertRedirects(response, reverse("works:detail", kwargs={"pk": activity.pk}))
        self.assertEqual(WorkActivity.objects.count(), 1)
