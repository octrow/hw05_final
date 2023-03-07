from django import forms
from django.test import Client, TestCase

from ..forms import User
from .const import AUTHOR, REVERSE_SIGNUP


class UsersViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=AUTHOR)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_page_show_correct_context(self):
        responce = self.authorized_client.get(REVERSE_SIGNUP)
        form_fields = {
            "first_name": forms.fields.CharField,
            "last_name": forms.fields.CharField,
            "username": forms.fields.CharField,
            "email": forms.fields.EmailField,
        }
        for field, expected_type in form_fields.items():
            with self.subTest(field=field):
                form_field = responce.context["form"].fields[field]
                self.assertIsInstance(form_field, expected_type)
