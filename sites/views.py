from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import DeleteMessageMixin
from inspections.models import Inspection
from sites.forms import SiteCreateForm, SiteDeleteForm, SiteEditForm, SiteFilterForm
from sites.models import ConstructionSite


class SiteListView(ListView):
    model = ConstructionSite
    template_name = "sites/site_list.html"
    context_object_name = "sites"
    paginate_by = 6

    def get_queryset(self):
        queryset = ConstructionSite.objects.all()
        self.filter_form = SiteFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data["q"].strip()
            status = self.filter_form.cleaned_data["status"]
            sort = self.filter_form.cleaned_data["sort"]

            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search)
                    | Q(city__icontains=search)
                    | Q(permit_number__icontains=search)
                )
            if status:
                queryset = queryset.filter(status=status)

            if sort == "name":
                queryset = queryset.order_by("name")
            elif sort == "newest":
                queryset = queryset.order_by("-start_date", "name")
            else:
                queryset = queryset.order_by("planned_end_date", "name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        if self.request.GET.get("q") or self.request.GET.get("status"):
            context["filters_applied"] = True
        return context


class SiteDetailView(DetailView):
    model = ConstructionSite
    template_name = "sites/site_detail.html"
    context_object_name = "site"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = self.object
        context["activities"] = site.activities.prefetch_related("contractors")
        context["open_inspections"] = Inspection.objects.filter(
            activity__site=site, is_resolved=False
        ).select_related("activity__site")
        return context


class SiteCreateView(SuccessMessageMixin, CreateView):
    model = ConstructionSite
    form_class = SiteCreateForm
    template_name = "sites/site_form.html"
    success_message = "The construction site was registered."


class SiteUpdateView(SuccessMessageMixin, UpdateView):
    model = ConstructionSite
    form_class = SiteEditForm
    template_name = "sites/site_form.html"
    context_object_name = "site"
    success_message = "The construction site was updated."


class SiteDeleteView(DeleteMessageMixin, DeleteView):
    model = ConstructionSite
    template_name = "sites/site_confirm_delete.html"
    context_object_name = "site"
    success_url = reverse_lazy("sites:list")
    success_message = "The construction site and its activities were deleted."
    protected_message = (
        "The site cannot be deleted because inspections are recorded for its activities. "
        "Delete the inspections first."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = self.object
        context["summary_form"] = SiteDeleteForm(instance=site)
        context["activity_count"] = site.activities.count()
        context["inspection_count"] = Inspection.objects.filter(activity__site=site).count()
        return context
