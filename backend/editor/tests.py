from pathlib import Path
from tempfile import TemporaryDirectory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse


class StartPageTests(SimpleTestCase):
    def test_start_page_offers_game_creation_and_import(self):
        response = self.client.get(reverse("start"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/start.html")
        self.assertContains(response, "Neues Spiel erstellen")
        self.assertContains(response, f'action="{reverse("new_game")}"')
        self.assertContains(response, f'action="{reverse("upload_json")}"')


class GuidedLevelCreationTests(TestCase):
    def test_guided_level(self):
        response = self.client.get(reverse("create_level"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/createLevel.html")

        session = self.client.session

        self.assertTrue(session["guided_level_creation"])

        self.assertEqual(
            session["new_level"],
            {
                "id": "",
                "levelPicture": "",
                "startDialog": "",
                "queryRestriction": {},
                "items": [],
                "databaseName": "",
            }
        )

        self.assertContains(response, "Hey, ich bin Cosmo")
        self.assertContains(response, "Start")

    def test_level1(self):
        self.client.get(reverse("create_level"))
        with TemporaryDirectory() as upload_root, self.settings(
            BASE_DIR=Path(upload_root)
        ):
            response = self.client.post(
                reverse("create_level1"),
                {
                    "level_name": "Level1",
                    "level_greeting": "Hallo",
                    "levelPicture": SimpleUploadedFile(
                        "bachelor.png", b"test image", content_type="image/png"
                    ),
                },
            )
            uploaded_picture = (
                Path(upload_root) / "editor/static/editor/img/levels/bachelor.png"
            )
            self.assertTrue(uploaded_picture.is_file())

        self.assertRedirects(
            response,
            reverse("create_level2")
        )

        new_level = self.client.session["new_level"]
        self.assertEqual(new_level["id"], "Level1")
        self.assertEqual(new_level["levelPicture"], "bachelor.png")
        self.assertEqual(new_level["startDialog"], "Hallo")

    def test_level2(self):
        self.client.get(reverse("create_level"))
        with TemporaryDirectory() as upload_root, self.settings(
            BASE_DIR=Path(upload_root)
        ):
            level1_page = self.client.get(reverse("create_level1"))
            self.assertEqual(level1_page.status_code, 200)
            self.assertTemplateUsed(level1_page, "editor/createLevel1.html")

            level1_response = self.client.post(
                reverse("create_level1"),
                {
                    "level_name": "Level1",
                    "level_greeting": "Hallo",
                    "levelPicture": SimpleUploadedFile(
                        "bachelor.png", b"test image", content_type="image/png"
                    ),
                },
            )
            self.assertRedirects(level1_response, reverse("create_level2"))

            level2_page = self.client.get(reverse("create_level2"))
            self.assertEqual(level2_page.status_code, 200)
            self.assertTemplateUsed(level2_page, "editor/createLevel2.html")

            level2_response = self.client.post(
                reverse("create_level2"),
                {
                    "max_rows": "5",
                    "max_columns": "5",
                    "too_many_rows_message": "Too many rows",
                    "too_many_columns_message": "Too many columns",
                    "too_many_rows_columns_message": "Too many rows and columns",
                },
            )
            self.assertRedirects(level2_response, reverse("create_level3"))

            uploaded_picture = (
                Path(upload_root) / "editor/static/editor/img/levels/bachelor.png"
            )
            self.assertTrue(uploaded_picture.is_file())

        new_level = self.client.session["new_level"]
        self.assertEqual(
            new_level,
            {
                "id": "Level1",
                "levelPicture": "bachelor.png",
                "databaseName": "Level1.db",
                "startDialog": "Hallo",
                "queryRestriction": {
                    "rowRestriction": {
                        "maxNumber": 5,
                        "violationMessages": ["Too many rows"],
                    },
                    "columnRestriction": {
                        "maxNumber": 5,
                        "violationMessages": ["Too many columns"],
                    },
                    "colAndRowViolationMessages": ["Too many rows and columns"],
                },
                "items": [],
            },
        )
