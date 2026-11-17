from django.urls import path

from works import reports, views

app_name = "works"

urlpatterns = [
    path("", views.ActivityListView.as_view(), name="list"),
    path("add/", views.ActivityCreateView.as_view(), name="create"),
    path("report/<int:site_pk>/", reports.site_report_csv, name="site-report"),
    path("<int:pk>/", views.ActivityDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ActivityUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ActivityDeleteView.as_view(), name="delete"),
]
