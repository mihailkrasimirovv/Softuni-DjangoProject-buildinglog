from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Landing page of BuildLog."""

    template_name = "common/home.html"


class AboutView(TemplateView):
    """Static page that explains how BuildLog is organised."""

    template_name = "common/about.html"
