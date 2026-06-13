from django.urls import path
from . import views

urlpatterns = [
    path("", views.start_page, name="start"),
    path("level/", views.level_view, name="level"),
    path("upload-json/", views.upload_json_view, name="upload_json"),
]