from http import HTTPStatus

from django.test import Client, TestCase

from .const import ABOUT_AUTHOR_URL, ABOUT_TECH_URL


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in (
            (ABOUT_AUTHOR_URL, "about/author.html"),
            (ABOUT_TECH_URL, "about/tech.html"),
        ):
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_public_access(self):
        """URL-адрес доступны любому пользователю."""
        for url in (
            ABOUT_AUTHOR_URL,
            ABOUT_TECH_URL,
        ):
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
