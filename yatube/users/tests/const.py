from django.urls import reverse

AUTHOR = "NewNameUser"
ANOTHERUSER = "AnotherUser"
GROUP_TITLE = "Тестовая группа"
GROUP_SLUG = "test_slug"
GROUP_DESCRIPTION = "Тестовое описание"
POST_TEXT = "Тестовая запись"

INDEX_URL = "/"
ABOUT_AUTHOR_URL = "/about/author/"
ABOUT_TECH_URL = "/about/tech/"
GROUP_URL = "/group/" + GROUP_SLUG + "/"
PROFILE_URL = "/profile/" + AUTHOR + "/"
CREATE_URL = "/create/"
POST_URL = "/posts/"
EDIT_URL = "/edit/"
UNEXISTING_URL = "/unexisting_url/"

REVERSE_SIGNUP = reverse("users:signup")
USER_DATA = {
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "username": ANOTHERUSER,
    "email": "testuser@example.com",
    "password1": "testpassword",
    "password2": "testpassword",
}
