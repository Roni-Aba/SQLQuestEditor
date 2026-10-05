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

    def level1(self):
        self.client.get(reverse("create_level"))
        response = self.client.post(
            reverse("create_level1"),
            {
                "level_name" : "Level1",
                "level_greeting" : "Hallo",
                "level_picture" : "/SQLQuestEditor/bachelor.png"
            }
        )
        self.assertRedirects(
            response,
            reverse("create_level2")
        )

        new_level = self.client.session["new_level"]
        self.assertEqual(new_level["id"], "Level1")
        self.assertEqual(new_level["levelPicture"], "/SQLQuestEditor/bachelor.png")
        self.assertEqual(new_level["startDialog"], "Hallo")
