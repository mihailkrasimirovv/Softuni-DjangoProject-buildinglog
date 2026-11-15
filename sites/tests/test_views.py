from django.test import TestCase
from django.urls import reverse

from common.tests.factories import make_site
from sites.models import ConstructionSite
from sites.tests.test_forms import site_form_data


class SiteViewsTests(TestCase):
    def test_list_shows_the_sites(self):
        make_site(name="Vitosha Park Residence")

        response = self.client.get(reverse("sites:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vitosha Park Residence")

    def test_list_search(self):
        make_site(name="Vitosha Park Residence", permit_number="RS-1/2026")
        make_site(name="Maritsa Logistics Hall", permit_number="RS-2/2026")

        response = self.client.get(reverse("sites:list"), {"q": "maritsa"})

        self.assertContains(response, "Maritsa Logistics Hall")
        self.assertNotContains(response, "Vitosha Park Residence")

    def test_create_site(self):
        response = self.client.post(reverse("sites:create"), site_form_data())

        site = ConstructionSite.objects.get()
        self.assertRedirects(response, reverse("sites:detail", kwargs={"pk": site.pk}))

    def test_create_with_errors_shows_the_form_again(self):
        data = site_form_data()
        data["permit_number"] = "wrong"

        response = self.client.post(reverse("sites:create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConstructionSite.objects.count(), 0)

    def test_edit_site(self):
        site = make_site()
        data = site_form_data()
        data["name"] = "New name"

        self.client.post(reverse("sites:edit", kwargs={"pk": site.pk}), data)

        site.refresh_from_db()
        self.assertEqual(site.name, "New name")

    def test_delete_site_after_confirmation(self):
        site = make_site()
        url = reverse("sites:delete", kwargs={"pk": site.pk})

        response = self.client.get(url)
        self.assertContains(response, "Yes, delete")
        self.assertEqual(ConstructionSite.objects.count(), 1)

        response = self.client.post(url)
        self.assertRedirects(response, reverse("sites:list"))
        self.assertEqual(ConstructionSite.objects.count(), 0)

    def test_missing_site_gives_404(self):
        response = self.client.get(reverse("sites:detail", kwargs={"pk": 999}))

        self.assertEqual(response.status_code, 404)
