from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from .const import (ANOTHERUSER, AUTHOR, GROUP_DESCRIPTION, GROUP_SLUG,
                    GROUP_TITLE, POST_TEXT, UNEXISTING_URL)


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.anotheruser = User.objects.create_user(username=ANOTHERUSER)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(StaticURLTests.anotheruser)
        self.urls_names = (
            ("posts:index", None, "/"),
            (
                "posts:group_list",
                (self.group.slug,),
                f"/group/{self.group.slug}/",
            ),
            (
                "posts:profile",
                (self.user.username,),
                f"/profile/{self.user.username}/",
            ),
            ("posts:post_detail", (self.post.id,), f"/posts/{self.post.id}/"),
            ("posts:post_create", None, "/create/"),
            (
                "posts:post_edit",
                (self.post.id,),
                f"/posts/{self.post.id}/edit/",
            ),
            ("posts:follow_index", None, "/follow/"),
            (
                "posts:profile_follow",
                (self.user.username,),
                f"/profile/{self.user.username}/follow/",
            ),
            (
                "posts:profile_unfollow",
                (self.user.username,),
                f"/profile/{self.user.username}/unfollow/",
            ),
            (
                "posts:add_comment",
                (self.post.id,),
                f"/posts/{self.post.id}/comment/",
            ),
            (
                "posts:post_delete",
                (self.post.id,),
                f"/posts/{self.post.id}/delete/",
            ),
        )

    def test_direct_urls_equal_reverse_urls(self):
        """URL-адрес соответствует reverse_urls."""
        for reverse_url, argument, url in self.urls_names:
            with self.subTest(url=url):
                self.assertEqual(reverse(reverse_url, args=argument), url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ("posts:index", None, "posts/index.html"),
            ("posts:group_list", (self.group.slug,), "posts/group_list.html"),
            ("posts:profile", (self.user.username,), "posts/profile.html"),
            ("posts:post_detail", (self.post.id,), "posts/post_detail.html"),
            ("posts:post_create", None, "posts/create_post.html"),
            ("posts:post_edit", (self.post.id,), "posts/create_post.html"),
            ("posts:follow_index", None, "posts/follow.html"),
        )
        for reverse_url, argument, template in templates_url_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(
                    reverse(reverse_url, args=argument)
                )
                self.assertTemplateUsed(response, template)

    def test_urls_404(self):
        """Несуществующий URL-адрес возвращает ошибку 404."""
        response = self.client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_all_urls_access_author(self):
        """Все URL-адреса доступны для авторизованного автора пользователя."""
        for reverse_url, argument, _ in self.urls_names:
            with self.subTest(reverse_url=reverse_url):
                if reverse_url == "posts:add_comment":
                    response = self.authorized_client.post(
                        reverse("posts:add_comment", args=(self.post.id,)),
                        {"text": "This is a test comment."},
                    )
                    self.assertRedirects(
                        response,
                        reverse("posts:post_detail", args=(self.post.id,)),
                    )
                else:
                    response = self.authorized_client.get(
                        reverse(reverse_url, args=argument)
                    )
                    if reverse_url == "posts:profile_follow":
                        self.assertRedirects(
                            response, reverse("posts:profile", args=argument)
                        )
                    elif reverse_url == "posts:profile_unfollow":
                        self.assertEqual(
                            response.status_code, HTTPStatus.NOT_FOUND
                        )
                    elif reverse_url == "posts:post_delete":
                        self.assertRedirects(
                            response,
                            reverse(
                                "posts:profile", args=(self.user.username,)
                            ),
                        )
                    else:
                        self.assertEqual(
                            self.authorized_client.get(
                                reverse(reverse_url, args=argument)
                            ).status_code,
                            HTTPStatus.OK,
                        )

    def test_urls_access_another_user(self):
        """URL-адреса доступные для другого пользователя."""
        for reverse_url, argument, _ in self.urls_names:
            with self.subTest(reverse_url=reverse_url):
                if reverse_url == "posts:add_comment":
                    response = self.another_authorized_client.post(
                        reverse("posts:add_comment", args=(self.post.id,)),
                        {"text": "This is a test comment."},
                    )
                    self.assertRedirects(
                        response,
                        reverse("posts:post_detail", args=(self.post.id,)),
                    )
                else:
                    response = self.another_authorized_client.get(
                        reverse(reverse_url, args=argument)
                    )
                    if reverse_url in ("posts:post_edit", "posts:post_delete"):
                        self.assertRedirects(
                            response,
                            reverse("posts:post_detail", args=argument),
                        )
                    elif reverse_url == "posts:profile_follow":
                        self.assertRedirects(
                            response,
                            reverse("posts:profile", args=argument),
                        )
                    elif reverse_url == "posts:profile_unfollow":
                        self.assertRedirects(
                            response, reverse("posts:profile", args=argument)
                        )
                    else:
                        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_access_guest(self):
        """URL-адреса доступны для неавторизованного пользователя."""
        names_list = [
            "posts:post_edit",
            "posts:post_create",
            "posts:post_delete",
            "posts:add_comment",
            "posts:follow_index",
            "posts:profile_follow",
            "posts:profile_unfollow",
        ]
        reverse_login = reverse("users:login")
        for reverse_url, argument, _ in self.urls_names:
            response = self.client.get(reverse(reverse_url, args=argument))
            if reverse_url not in names_list:
                with self.subTest(reverse_url=reverse_url):
                    self.assertEqual(response.status_code, HTTPStatus.OK)
            else:
                url_argument = reverse(reverse_url, args=argument)
                excepted_redirect = f"{reverse_login}?next={url_argument}"
                self.assertRedirects(response, excepted_redirect)
