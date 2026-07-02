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
    path("createLevel51/", views.create_level51_view, name="create_level51"),
    path("createLevel6/",views.create_level6_view, name="create_level6"),
    path("createLevel61/", views.create_level61_view, name="create_level61"),
    path("createLevel6hint/", views.create_level6hint_view, name="create_level6hint"),
    path("createLevel6exit/", views.create_level6exit_view, name="create_level6exit"),
    path("createLevel6table/",views.create_level6table_view, name="create_level6table"),
    path("createLevel7/", views.create_level7_view, name="create_level7"),
    path("createLevel8/", views.create_level8_view, name="create_level8"),
]