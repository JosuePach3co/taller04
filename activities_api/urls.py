from django.urls import path
from . import views

urlpatterns = [
    path("", views.ActivitiesListCreate.as_view(), name="activities_list_create"),
    path("<str:activity_id>/", views.ActivityDetail.as_view(), name="activity_detail"),
]
