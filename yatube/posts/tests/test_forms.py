import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User
from .const import (
    AUTHOR,
    COMMENT_TEXT,
    GROUP_DESCRIPTION,
    GROUP_DESCRIPTION_2,
    GROUP_SLUG,
    GROUP_SLUG_2,
    GROUP_TITLE,
    GROUP_TITLE_2,
    ONE,
    POST_TEXT,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_2,
            slug=GROUP_SLUG_2,
            description=GROUP_DESCRIPTION_2,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form_valid_data(self):
        """Форма создает пост в указанном группе."""
        Post.objects.all().delete()
        count_posts = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00"
            b"\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        image_upload = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": POST_TEXT,
            "group": self.group.id,
            "image": image_upload,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        post = Post.objects.first()
        self.assertRedirects(
            response, reverse("posts:profile", args=(self.user.username,))
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.image.name, "posts/small.gif")
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
                author=self.user,
                group=self.group,
                image="posts/small.gif",
            ).exists()
        )
        self.assertEqual(Post.objects.count(), count_posts + ONE)

    def test_create_comment_authorizet(self):
        """Форма создает комментарий в указанном посте."""
        Comment.objects.all().delete()
        count_comments = Comment.objects.count()
        form_data = {
            "text": COMMENT_TEXT,
            "author": self.user.id,
            "post": self.post.id,
        }
        response = self.authorized_client.post(
            reverse("posts:add_comment", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertRedirects(
            response, reverse("posts:post_detail", args=(form_data["post"],))
        )
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.author.id, form_data["author"])
        self.assertEqual(count_comments + ONE, Comment.objects.count())

    def test_edit_post_correct(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": POST_TEXT + "отредактированный",
            "group": self.group_2.id,
        }
        self.authorized_client.post(
            reverse("posts:post_edit", args=[ONE]),
            data=form_data,
            follow=True,
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(Post.objects.count(), posts_count)
        response = self.authorized_client.get(
            reverse("posts:group_list", args=[GROUP_SLUG])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_access_post_create(self):
        """Не доступно для гостевого пользователя."""
        posts_count = Post.objects.count()
        form_data = {
            "text": POST_TEXT,
            "group": self.group.id,
        }
        self.guest_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_access_post_edit(self):
        """Не доступно для гостевого пользователя."""
        form_data = {
            "text": POST_TEXT + "невозможный",
            "group": self.group_2.id,
        }
        self.guest_client.post(
            reverse("posts:post_edit", args=[ONE]),
            data=form_data,
            follow=True,
        )
        post = Post.objects.first()
        self.assertNotEqual(post.text, form_data["text"])
