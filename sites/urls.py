from django.urls import path

from sites import views

app_name = "sites"

urlpatterns = [
    path("", views.SiteListView.as_view(), name="list"),
    path("add/", views.SiteCreateView.as_view(), name="create"),
    path("<int:pk>/", views.SiteDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.SiteUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.SiteDeleteView.as_view(), name="delete"),
]
