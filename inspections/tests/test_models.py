from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from common.tests.factories import days_from_today, make_activity, make_inspection, make_site


class InspectionModelTests(TestCase):
    def setUp(self):
        self.activity = make_activity(make_site())
        self.inspection = make_inspection(self.activity)

    def test_resolve_and_reopen(self):
        self.inspection.resolve(days_from_today(0), "Spacers were installed.")
        self.assertTrue(self.inspection.is_resolved)

        self.inspection.reopen()
        self.assertFalse(self.inspection.is_resolved)
        self.assertIsNone(self.inspection.resolved_on)

    def test_resolution_cannot_be_before_the_inspection(self):
        self.inspection.resolve(days_from_today(-30), "Fixed before it was found.")

        with self.assertRaises(ValidationError):
            self.inspection.full_clean()

    def test_is_overdue(self):
        self.assertFalse(self.inspection.is_overdue)

        self.inspection.due_date = days_from_today(-1)
        self.assertTrue(self.inspection.is_overdue)

    def test_activity_with_inspections_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            self.activity.delete()
