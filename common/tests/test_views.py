from django.test import TestCase
from django.urls import reverse


class CommonPagesTests(TestCase):
    def test_home_page_is_displayed(self):
        response = self.client.get(reverse("common:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "common/home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_about_page_is_displayed(self):
        response = self.client.get(reverse("common:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "common/about.html")

    def test_unknown_url_shows_the_custom_404_page(self):
        response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "not on the site plan", status_code=404)
