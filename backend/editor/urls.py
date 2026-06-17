from django.urls import path
from . import views

urlpatterns = [
    path("", views.start_page, name="start"),
    path("level/", views.level_view, name="level"),
    path("upload-json/", views.upload_json_view, name="upload_json"),
    path("components/", views.component_test_view, name="component_test"),
    path("createLevel/", views.create_level, name="create_level"),
    path("auswahl/", views.auswahl_view, name="auswahl_view"),]