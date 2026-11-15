from django.urls import path

from contractors import views

app_name = "contractors"

urlpatterns = [
    path("", views.ContractorListView.as_view(), name="list"),
    path("add/", views.ContractorCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ContractorDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ContractorUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ContractorDeleteView.as_view(), name="delete"),
]
