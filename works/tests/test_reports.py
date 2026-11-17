from django.test import TestCase
from django.urls import reverse

from common.tests.factories import make_activity, make_site


class SiteReportTests(TestCase):
    def test_report_contains_the_activities_of_the_site(self):
        site = make_site()
        make_activity(site, title="Foundation slab", progress=100)

        response = self.client.get(reverse("works:site-report", kwargs={"site_pk": site.pk}))
        text = response.content.decode("utf-8-sig")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("Foundation slab", text)
        self.assertIn("Completed", text)

    def test_report_for_missing_site_gives_404(self):
        response = self.client.get(reverse("works:site-report", kwargs={"site_pk": 999}))

        self.assertEqual(response.status_code, 404)
