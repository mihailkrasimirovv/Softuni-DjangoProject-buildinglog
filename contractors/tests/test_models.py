from django.core.exceptions import ValidationError
from django.test import TestCase

from common.tests.factories import make_contractor


class ContractorModelTests(TestCase):
    def test_str_is_the_company_name(self):
        contractor = make_contractor(company_name="Balkan Stroy Ltd.")

        self.assertEqual(str(contractor), "Balkan Stroy Ltd.")

    def test_eik_with_13_digits_is_valid(self):
        contractor = make_contractor(eik="2034567890001")

        contractor.full_clean()

    def test_wrong_eik_is_not_valid(self):
        contractor = make_contractor()
        contractor.eik = "12345"

        with self.assertRaises(ValidationError):
            contractor.full_clean()

    def test_wrong_name_and_phone_are_not_valid(self):
        contractor = make_contractor()
        contractor.contact_person = "Ivan 2"
        contractor.phone = "call me"

        with self.assertRaises(ValidationError) as context:
            contractor.full_clean()

        self.assertIn("contact_person", context.exception.message_dict)
        self.assertIn("phone", context.exception.message_dict)
