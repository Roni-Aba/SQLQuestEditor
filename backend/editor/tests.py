from django.test import SimpleTestCase
from django.urls import reverse


class StartPageTests(SimpleTestCase):
    def test_start_page_loads(self):
        response = self.client.get(reverse("start"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "editor/start.html")
