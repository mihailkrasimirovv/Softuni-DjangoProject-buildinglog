from django.urls import path

from works import views

app_name = "works"

urlpatterns = [
    path("", views.ActivityListView.as_view(), name="list"),
    path("add/", views.ActivityCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ActivityDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ActivityUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ActivityDeleteView.as_view(), name="delete"),
]
