from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import DeleteMessageMixin
from contractors.forms import (
    ContractorCreateForm,
    ContractorDeleteForm,
    ContractorEditForm,
    ContractorFilterForm,
)
from contractors.models import Contractor


class ContractorListView(ListView):
    model = Contractor
    template_name = "contractors/contractor_list.html"
    context_object_name = "contractors"
    paginate_by = 10

    def get_queryset(self):
        queryset = Contractor.objects.all()
        self.filter_form = ContractorFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data["q"].strip()
            trade = self.filter_form.cleaned_data["trade"]
            availability = self.filter_form.cleaned_data["activity"]

            if search:
                queryset = queryset.filter(
                    Q(company_name__icontains=search)
                    | Q(eik__icontains=search)
                    | Q(contact_person__icontains=search)
                )
            if trade:
                queryset = queryset.filter(trade=trade)
            if availability == "active":
                queryset = queryset.filter(is_active=True)
            elif availability == "inactive":
                queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        request_data = self.request.GET
        if request_data.get("q") or request_data.get("trade") or request_data.get("activity"):
            context["filters_applied"] = True
        return context


class ContractorDetailView(DetailView):
    model = Contractor
    template_name = "contractors/contractor_detail.html"
    context_object_name = "contractor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = self.object.activities.select_related("site")
        context["activities"] = activities.prefetch_related("contractors")
        return context


class ContractorCreateView(SuccessMessageMixin, CreateView):
    model = Contractor
    form_class = ContractorCreateForm
    template_name = "contractors/contractor_form.html"
    success_message = "The contractor was added."


class ContractorUpdateView(SuccessMessageMixin, UpdateView):
    model = Contractor
    form_class = ContractorEditForm
    template_name = "contractors/contractor_form.html"
    context_object_name = "contractor"
    success_message = "The contractor was updated."


class ContractorDeleteView(DeleteMessageMixin, DeleteView):
    model = Contractor
    template_name = "contractors/contractor_confirm_delete.html"
    context_object_name = "contractor"
    success_url = reverse_lazy("contractors:list")
    success_message = "The contractor was deleted."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary_form"] = ContractorDeleteForm(instance=self.object)
        context["activity_count"] = self.object.activities.count()
        return context
