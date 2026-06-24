from django.urls import path
from . import views

urlpatterns = [
    path("", views.start_page, name="start"),
    path("level/", views.level_view, name="level"),
    path("upload-json/", views.upload_json_view, name="upload_json"),
    path("components/", views.component_test_view, name="component_test"),
    path("createLevel/", views.create_level, name="create_level"),
    path("auswahl/", views.auswahl_view, name="auswahl_view"),
    path("createLevel1/", views.create_level1_view, name="create_level1"),
    path("createLevel2/", views.create_level2_view, name="create_level2"),
    path("createLevel3/", views.create_level3_view, name="create_level3"),
    path("createLevel4/", views.create_level4_view, name="create_level4"),
    path("createLevel4-1/", views.create_level41_view, name="create_level41"),  # ← NEW
    path("createLevel4-2/", views.create_level42_view, name="create_level42"),
    path("createLevel5/", views.create_level5_view, name="create_level5"),
]