from django.urls import path

from inspections import views

app_name = "inspections"

urlpatterns = [
    path("", views.InspectionListView.as_view(), name="list"),
    path("add/", views.InspectionCreateView.as_view(), name="create"),
    path("<int:pk>/", views.InspectionDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.InspectionUpdateView.as_view(), name="edit"),
    path("<int:pk>/resolve/", views.InspectionResolveView.as_view(), name="resolve"),
    path("<int:pk>/reopen/", views.reopen_inspection, name="reopen"),
    path("<int:pk>/delete/", views.InspectionDeleteView.as_view(), name="delete"),
]
