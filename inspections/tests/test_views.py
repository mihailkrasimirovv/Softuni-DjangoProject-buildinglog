from django.test import TestCase
from django.urls import reverse

from common.tests.factories import days_from_today, make_activity, make_inspection, make_site
from inspections.models import Inspection
from inspections.tests.test_forms import inspection_form_data


class InspectionViewsTests(TestCase):
    def setUp(self):
        self.activity = make_activity(make_site())

    def test_list_filter_by_severity(self):
        make_inspection(self.activity, title="Cracks in the plaster", severity="low")
        make_inspection(self.activity, title="Missing railing", severity="critical")

        response = self.client.get(reverse("inspections:list"), {"severity": "critical"})

        self.assertContains(response, "Missing railing")
        self.assertNotContains(response, "Cracks in the plaster")

    def test_create_inspection(self):
        response = self.client.post(
            reverse("inspections:create"), inspection_form_data(self.activity)
        )

        inspection = Inspection.objects.get()
        self.assertRedirects(response, reverse("inspections:detail", kwargs={"pk": inspection.pk}))

    def test_resolve_and_reopen_inspection(self):
        inspection = make_inspection(self.activity)
        data = {
            "resolved_on": days_from_today(0),
            "resolution_note": "Spacers were installed and checked.",
        }

        self.client.post(reverse("inspections:resolve", kwargs={"pk": inspection.pk}), data)
        inspection.refresh_from_db()
        self.assertTrue(inspection.is_resolved)

        self.client.post(reverse("inspections:reopen", kwargs={"pk": inspection.pk}))
        inspection.refresh_from_db()
        self.assertFalse(inspection.is_resolved)

    def test_reopen_works_only_with_post(self):
        inspection = make_inspection(self.activity)

        response = self.client.get(reverse("inspections:reopen", kwargs={"pk": inspection.pk}))

        self.assertEqual(response.status_code, 405)

    def test_delete_inspection(self):
        inspection = make_inspection(self.activity)

        response = self.client.post(reverse("inspections:delete", kwargs={"pk": inspection.pk}))

        self.assertRedirects(response, reverse("inspections:list"))
        self.assertEqual(Inspection.objects.count(), 0)
