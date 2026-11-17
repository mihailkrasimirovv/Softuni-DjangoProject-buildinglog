from django.test import TestCase
from django.urls import reverse

from common.tests.factories import make_activity, make_contractor, make_inspection, make_site


class DashboardTests(TestCase):
    def test_empty_dashboard(self):
        response = self.client.get(reverse("common:home"))

        self.assertContains(response, "Welcome to BuildLog")
        self.assertEqual(response.context["stats"]["sites_total"], 0)

    def test_dashboard_numbers(self):
        site = make_site()
        make_site(name="Finished hall", permit_number="RS-2/2026", status="completed")
        make_contractor()
        activity = make_activity(site)
        make_inspection(activity, severity="critical")

        response = self.client.get(reverse("common:home"))
        stats = response.context["stats"]

        self.assertEqual(stats["sites_total"], 2)
        self.assertEqual(stats["sites_active"], 1)
        self.assertEqual(stats["contractors_active"], 1)
        self.assertEqual(stats["activities_total"], 1)
        self.assertEqual(stats["inspections_open"], 1)
        self.assertEqual(stats["inspections_critical"], 1)

    def test_stage_summary(self):
        site = make_site()
        make_activity(site, title="First", progress=100)
        make_activity(site, title="Second", progress=50)

        response = self.client.get(reverse("common:home"))
        summary = response.context["stage_summary"]

        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["label"], "Structure")
        self.assertEqual(summary[0]["total"], 2)
        self.assertEqual(summary[0]["average"], 75)
