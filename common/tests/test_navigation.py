from django.test import TestCase
from django.urls import reverse

from common.tests.factories import make_activity, make_contractor, make_inspection, make_site


class NavigationTests(TestCase):
    """Opens every page and checks that it works and has the menu and the footer."""

    def test_all_pages_open(self):
        site = make_site()
        contractor = make_contractor()
        activity = make_activity(site)
        inspection = make_inspection(activity)

        urls = [
            reverse("common:home"),
            reverse("common:about"),
            reverse("sites:list"),
            reverse("sites:create"),
            reverse("sites:detail", kwargs={"pk": site.pk}),
            reverse("sites:edit", kwargs={"pk": site.pk}),
            reverse("sites:delete", kwargs={"pk": site.pk}),
            reverse("contractors:list"),
            reverse("contractors:create"),
            reverse("contractors:detail", kwargs={"pk": contractor.pk}),
            reverse("contractors:edit", kwargs={"pk": contractor.pk}),
            reverse("contractors:delete", kwargs={"pk": contractor.pk}),
            reverse("works:list"),
            reverse("works:create"),
            reverse("works:detail", kwargs={"pk": activity.pk}),
            reverse("works:edit", kwargs={"pk": activity.pk}),
            reverse("works:delete", kwargs={"pk": activity.pk}),
            reverse("inspections:list"),
            reverse("inspections:create"),
            reverse("inspections:detail", kwargs={"pk": inspection.pk}),
            reverse("inspections:edit", kwargs={"pk": inspection.pk}),
            reverse("inspections:resolve", kwargs={"pk": inspection.pk}),
            reverse("inspections:delete", kwargs={"pk": inspection.pk}),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            self.assertContains(response, 'id="main-navigation"')
            self.assertContains(response, 'class="site-footer')
