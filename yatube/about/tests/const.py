from django.urls import reverse

ABOUT_AUTHOR_URL = "/about/author/"
ABOUT_TECH_URL = "/about/tech/"

REVERSE_AUTHOR = reverse("about:author")
REVERSE_TECH = reverse("about:tech")
