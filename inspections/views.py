from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import DeleteMessageMixin
from inspections.forms import (
    InspectionCreateForm,
    InspectionDeleteForm,
    InspectionEditForm,
    InspectionFilterForm,
    InspectionResolveForm,
)
from inspections.models import Inspection
from works.models import WorkActivity


class InspectionListView(ListView):
    model = Inspection
    template_name = "inspections/inspection_list.html"
    context_object_name = "inspections"
    paginate_by = 8

    def get_queryset(self):
        queryset = Inspection.objects.select_related("activity__site")
        self.filter_form = InspectionFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            site = self.filter_form.cleaned_data["site"]
            severity = self.filter_form.cleaned_data["severity"]
            state = self.filter_form.cleaned_data["state"]
            sort = self.filter_form.cleaned_data["sort"]

            if site:
                queryset = queryset.filter(activity__site=site)
            if severity:
                queryset = queryset.filter(severity=severity)

            if state == "open":
                queryset = queryset.filter(is_resolved=False)
            elif state == "resolved":
                queryset = queryset.filter(is_resolved=True)
            elif state == "overdue":
                queryset = queryset.filter(is_resolved=False, due_date__lt=timezone.localdate())

            if sort == "newest":
                queryset = queryset.order_by("-inspected_on", "-id")
            elif sort == "oldest":
                queryset = queryset.order_by("inspected_on", "id")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        for name in ["site", "severity", "state"]:
            if self.request.GET.get(name):
                context["filters_applied"] = True
        return context


class InspectionDetailView(DetailView):
    model = Inspection
    template_name = "inspections/inspection_detail.html"
    context_object_name = "inspection"


class InspectionCreateView(SuccessMessageMixin, CreateView):
    model = Inspection
    form_class = InspectionCreateForm
    template_name = "inspections/inspection_form.html"
    success_message = "The inspection was recorded."

    def get_initial(self):
        # when the page is opened from an activity (?activity=3) it is selected in the form
        initial = super().get_initial()
        activity_id = self.request.GET.get("activity", "")
        if activity_id.isdigit():
            initial["activity"] = int(activity_id)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_activities"] = WorkActivity.objects.exists()
        return context


class InspectionUpdateView(SuccessMessageMixin, UpdateView):
    model = Inspection
    form_class = InspectionEditForm
    template_name = "inspections/inspection_form.html"
    context_object_name = "inspection"
    success_message = "The inspection was updated."


class InspectionResolveView(SuccessMessageMixin, UpdateView):
    """Marks an open inspection as resolved. A resolved one gives 404 here."""

    queryset = Inspection.objects.filter(is_resolved=False)
    form_class = InspectionResolveForm
    template_name = "inspections/inspection_resolve.html"
    context_object_name = "inspection"
    success_message = "The inspection was marked as resolved."


@require_POST
def reopen_inspection(request, pk):
    """Opens a resolved inspection again. It changes data, so only POST is allowed."""
    inspection = get_object_or_404(Inspection, pk=pk, is_resolved=True)
    inspection.reopen()
    inspection.save()
    messages.warning(request, "The inspection was reopened.")
    return redirect("inspections:detail", pk=inspection.pk)


class InspectionDeleteView(DeleteMessageMixin, DeleteView):
    model = Inspection
    template_name = "inspections/inspection_confirm_delete.html"
    context_object_name = "inspection"
    success_url = reverse_lazy("inspections:list")
    success_message = "The inspection was deleted."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary_form"] = InspectionDeleteForm(instance=self.object)
        return context
