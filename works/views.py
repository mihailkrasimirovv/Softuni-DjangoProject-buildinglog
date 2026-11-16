from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from common.mixins import DeleteMessageMixin
from sites.models import ConstructionSite
from works.forms import (
    ActivityCreateForm,
    ActivityDeleteForm,
    ActivityEditForm,
    ActivityFilterForm,
)
from works.models import WorkActivity


class ActivityListView(ListView):
    model = WorkActivity
    template_name = "works/activity_list.html"
    context_object_name = "activities"
    paginate_by = 10

    def get_queryset(self):
        queryset = WorkActivity.objects.select_related("site").prefetch_related("contractors")
        self.filter_form = ActivityFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            search = self.filter_form.cleaned_data["q"].strip()
            site = self.filter_form.cleaned_data["site"]
            stage = self.filter_form.cleaned_data["stage"]
            state = self.filter_form.cleaned_data["state"]
            sort = self.filter_form.cleaned_data["sort"]
            today = timezone.localdate()

            if search:
                queryset = queryset.filter(title__icontains=search)
            if site:
                queryset = queryset.filter(site=site)
            if stage:
                queryset = queryset.filter(stage=stage)

            # the state is not saved in the database, it depends on the dates and the progress
            if state == "completed":
                queryset = queryset.filter(progress=100)
            elif state == "upcoming":
                queryset = queryset.filter(progress__lt=100, start_date__gt=today)
            elif state == "delayed":
                queryset = queryset.filter(progress__lt=100, end_date__lt=today)
            elif state == "in_progress":
                queryset = queryset.filter(
                    progress__lt=100, start_date__lte=today, end_date__gte=today
                )

            if sort == "deadline":
                queryset = queryset.order_by("end_date", "title")
            elif sort == "stage":
                queryset = queryset.order_by("stage", "start_date")
            elif sort == "progress":
                queryset = queryset.order_by("progress", "end_date")
            else:
                queryset = queryset.order_by("start_date", "title")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        for name in ["q", "site", "stage", "state"]:
            if self.request.GET.get(name):
                context["filters_applied"] = True
        return context


class ActivityDetailView(DetailView):
    model = WorkActivity
    template_name = "works/activity_detail.html"
    context_object_name = "activity"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contractors"] = self.object.contractors.all()
        context["inspections"] = self.object.inspections.select_related("activity__site")
        return context


class ActivityCreateView(SuccessMessageMixin, CreateView):
    model = WorkActivity
    form_class = ActivityCreateForm
    template_name = "works/activity_form.html"
    success_message = "The activity was added."

    def get_initial(self):
        # when the page is opened from a site (?site=5) that site is selected in the form
        initial = super().get_initial()
        site_id = self.request.GET.get("site", "")
        if site_id.isdigit():
            initial["site"] = int(site_id)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_sites"] = ConstructionSite.objects.exclude(status="completed").exists()
        return context


class ActivityUpdateView(SuccessMessageMixin, UpdateView):
    model = WorkActivity
    form_class = ActivityEditForm
    template_name = "works/activity_form.html"
    context_object_name = "activity"
    success_message = "The activity was updated."


class ActivityDeleteView(DeleteMessageMixin, DeleteView):
    model = WorkActivity
    template_name = "works/activity_confirm_delete.html"
    context_object_name = "activity"
    success_message = "The activity was deleted."
    protected_message = (
        "The activity cannot be deleted because inspections are recorded for it. "
        "Delete the inspections first."
    )

    def get_success_url(self):
        # go back to the site of the deleted activity
        return self.object.site.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary_form"] = ActivityDeleteForm(instance=self.object)
        context["inspection_count"] = self.object.inspections.count()
        return context
