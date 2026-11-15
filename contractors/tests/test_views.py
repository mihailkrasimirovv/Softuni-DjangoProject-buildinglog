from django.test import TestCase
from django.urls import reverse

from common.tests.factories import make_contractor
from contractors.models import Contractor
from contractors.tests.test_forms import contractor_form_data


class ContractorViewsTests(TestCase):
    def test_list_filter_by_availability(self):
        make_contractor(company_name="Geo Point", eik="111222333")
        make_contractor(company_name="Beton Pro", eik="444555666", is_active=False)

        response = self.client.get(reverse("contractors:list"), {"activity": "inactive"})

        self.assertContains(response, "Beton Pro")
        self.assertNotContains(response, "Geo Point")

    def test_create_contractor(self):
        response = self.client.post(reverse("contractors:create"), contractor_form_data())

        contractor = Contractor.objects.get()
        self.assertRedirects(response, reverse("contractors:detail", kwargs={"pk": contractor.pk}))

    def test_edit_contractor(self):
        contractor = make_contractor()
        data = contractor_form_data()
        data["contact_person"] = "Petar Ivanov"

        self.client.post(reverse("contractors:edit", kwargs={"pk": contractor.pk}), data)

        contractor.refresh_from_db()
        self.assertEqual(contractor.contact_person, "Petar Ivanov")

    def test_delete_contractor(self):
        contractor = make_contractor()

        response = self.client.post(reverse("contractors:delete", kwargs={"pk": contractor.pk}))

        self.assertRedirects(response, reverse("contractors:list"))
        self.assertEqual(Contractor.objects.count(), 0)
