import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from common.templatetags.buildlog_tags import badge_class, deadline_label, progress_bar


class TemplateTagsTests(SimpleTestCase):
    def test_badge_class_for_known_and_unknown_value(self):
        self.assertEqual(badge_class("completed"), "text-bg-success")
        self.assertEqual(badge_class("something else"), "text-bg-light")

    def test_deadline_label(self):
        today = timezone.localdate()

        self.assertEqual(deadline_label(today), "due today")
        self.assertEqual(deadline_label(today + datetime.timedelta(days=1)), "1 day left")
        self.assertEqual(deadline_label(today + datetime.timedelta(days=12)), "12 days left")
        self.assertEqual(deadline_label(today - datetime.timedelta(days=3)), "3 days overdue")
        self.assertEqual(deadline_label(None), "")

    def test_progress_bar_colour(self):
        self.assertEqual(progress_bar(100)["colour"], "bg-success")
        self.assertEqual(progress_bar(60)["colour"], "bg-primary")
        self.assertEqual(progress_bar(10)["colour"], "bg-warning")
        self.assertEqual(progress_bar(None)["percent"], 0)
