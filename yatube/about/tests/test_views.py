from http import HTTPStatus

from django.test import Client, TestCase

from .const import REVERSE_AUTHOR, REVERSE_TECH


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени доступен."""
        templates_urls = (
            (REVERSE_AUTHOR, HTTPStatus.OK),
            (REVERSE_TECH, HTTPStatus.OK),
        )
        for url, status_code in templates_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_about_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            "about/author.html": REVERSE_AUTHOR,
            "about/tech.html": REVERSE_TECH,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
