from django.test import SimpleTestCase
from django.urls import reverse


class StartPageTests(SimpleTestCase):
    def test_start_page_offers_game_creation_and_import(self):
        response = self.client.get(reverse("start"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/start.html")
        self.assertContains(response, "Neues Spiel erstellen")
        self.assertContains(response, f'action="{reverse("new_game")}"')
        self.assertContains(response, f'action="{reverse("upload_json")}"')
