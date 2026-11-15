from django.test import TestCase

from common.tests.factories import make_activity, make_contractor, make_site
from contractors.forms import ContractorCreateForm, ContractorEditForm


def contractor_form_data():
    return {
        "company_name": "Balkan Stroy Ltd.",
        "eik": "203456789",
        "trade": "concrete",
        "contact_person": "Ivan Petrov",
        "phone": "+359 888 123 456",
        "email": "Office@BalkanStroy.bg",
        "is_active": "on",
        "notes": "",
    }


class ContractorFormTests(TestCase):
    def test_valid_form_cleans_phone_and_email(self):
        form = ContractorCreateForm(contractor_form_data())

        self.assertTrue(form.is_valid())
        contractor = form.save()
        self.assertEqual(contractor.phone, "+359888123456")
        self.assertEqual(contractor.email, "office@balkanstroy.bg")

    def test_wrong_eik(self):
        data = contractor_form_data()
        data["eik"] = "12345"
        form = ContractorCreateForm(data)

        self.assertEqual(form.errors["eik"], ["The EIK must contain exactly 9 or 13 digits."])

    def test_eik_cannot_be_changed_in_the_edit_form(self):
        contractor = make_contractor(eik="111111111")
        data = contractor_form_data()
        data["eik"] = "999999999"
        form = ContractorEditForm(data, instance=contractor)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().eik, "111111111")

    def test_contractor_with_unfinished_work_cannot_be_deactivated(self):
        contractor = make_contractor()
        activity = make_activity(make_site(), progress=30)
        activity.contractors.add(contractor)
        data = contractor_form_data()
        del data["is_active"]
        form = ContractorEditForm(data, instance=contractor)

        self.assertIn("is_active", form.errors)
