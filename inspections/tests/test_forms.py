from django.test import TestCase

from common.tests.factories import days_from_today, make_activity, make_inspection, make_site
from inspections.forms import InspectionCreateForm, InspectionResolveForm


def inspection_form_data(activity):
    return {
        "activity": activity.pk,
        "title": "Missing rebar spacers",
        "inspector": "Maria Georgieva",
        "inspected_on": days_from_today(-3),
        "severity": "medium",
        "finding": "Spacers are missing under the bottom reinforcement.",
        "due_date": days_from_today(7),
    }


class InspectionFormTests(TestCase):
    def setUp(self):
        self.activity = make_activity(make_site())

    def test_valid_form(self):
        form = InspectionCreateForm(inspection_form_data(self.activity))

        self.assertTrue(form.is_valid())
        self.assertFalse(form.save().is_resolved)

    def test_create_form_has_no_resolution_fields(self):
        form = InspectionCreateForm()

        self.assertNotIn("resolved_on", form.fields)
        self.assertNotIn("resolution_note", form.fields)

    def test_inspection_date_in_the_future(self):
        data = inspection_form_data(self.activity)
        data["inspected_on"] = days_from_today(1)
        data["due_date"] = ""
        form = InspectionCreateForm(data)

        self.assertEqual(
            form.errors["inspected_on"], ["The inspection date cannot be in the future."]
        )

    def test_deadline_before_the_inspection(self):
        data = inspection_form_data(self.activity)
        data["due_date"] = days_from_today(-4)
        form = InspectionCreateForm(data)

        self.assertIn("due_date", form.errors)

    def test_critical_finding_needs_a_deadline(self):
        data = inspection_form_data(self.activity)
        data["severity"] = "critical"
        data["due_date"] = ""
        form = InspectionCreateForm(data)

        self.assertEqual(form.errors["due_date"], ["A critical finding must have a deadline."])

    def test_resolve_form(self):
        inspection = make_inspection(self.activity)
        data = {
            "resolved_on": days_from_today(0),
            "resolution_note": "Spacers were installed and checked.",
        }
        form = InspectionResolveForm(data, instance=inspection)

        self.assertTrue(form.is_valid())
        self.assertTrue(form.save().is_resolved)

    def test_resolve_form_needs_date_and_note(self):
        inspection = make_inspection(self.activity)
        form = InspectionResolveForm({}, instance=inspection)

        self.assertIn("resolved_on", form.errors)
        self.assertIn("resolution_note", form.errors)
