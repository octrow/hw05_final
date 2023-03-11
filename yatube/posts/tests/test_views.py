import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post, User
from .const import (ANOTHERUSER, AUTHOR, COMMENT_TEXT, GROUP_DESCRIPTION,
                    GROUP_DESCRIPTION_2, GROUP_SLUG, GROUP_SLUG_2, GROUP_TITLE,
                    GROUP_TITLE_2, POST_TEXT, PUB_DATE, THIRDUSER, THIRTEEN)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE, slug=GROUP_SLUG, description=GROUP_DESCRIPTION
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.image_upload = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.group_2 = Group.objects.create(
            title=GROUP_TITLE_2,
            slug=GROUP_SLUG_2,
            description=GROUP_DESCRIPTION_2,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT + "testpostcontent",
            author=cls.user,
            group=cls.group,
            pub_date=PUB_DATE,
            image=cls.image_upload,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=COMMENT_TEXT,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_context(self, query, is_post=False):
        """Проверка контекста поста"""
        if is_post:
            post = query.context["post"]
        else:
            post = query.context["page_obj"][0]
        self.assertEqual(post.id, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author.id, self.user.id)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.image, f"posts/{self.image_upload}")

    def test_index_grouplist_profile_show_correct_content(self):
        """Шаблоны index, group_list, profile
        сформированы с правильным контекстом."""
        pages_name = (
            ("posts:index", None),
            ("posts:group_list", (self.group.slug,)),
            ("posts:profile", (self.user.username,)),
        )
        for reverse_name, argument in pages_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse(reverse_name, args=argument)
                )
                self.check_context(response)
                if reverse_name == "posts:group_list":
                    self.assertEqual(response.context["group"], self.group)
                if reverse_name == "posts:profile":
                    self.assertEqual(response.context["author"], self.user)

    def test_post_detail_show_correct_content(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", args=(self.post.id,))
        )
        self.check_context(response, True)
        self.assertEqual(response.context["comments"][0], self.comment)

    def test_create_post_and_post_edit_show_correct_content(self):
        """Шаблон create_post.html сформированы с правильным контекстом."""
        templates_name_pages = (
            ("posts:post_create", None),
            ("posts:post_edit", (self.post.id,)),
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for page, argument in templates_name_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse(page, args=argument)
                )
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], PostForm)
                for field, field_type in form_fields.items():
                    with self.subTest(field=field):
                        form_field = response.context["form"].fields[field]
                        self.assertIsInstance(form_field, field_type)

    def test_check_post_correct_group_page(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", args=(self.group.slug,))
        )
        self.assertEqual(len(response.context["page_obj"]), 1)
        response = self.authorized_client.get(
            reverse("posts:group_list", args=(self.group_2.slug,))
        )
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_cache_index_page(self):
        response1 = self.authorized_client.get(reverse("posts:index"))
        Post.objects.all().delete()
        response2 = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(response1.content, response3.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.anotheruser = User.objects.create_user(username=ANOTHERUSER)
        cls.follower = Follow.objects.create(
            user=cls.anotheruser, author=cls.user
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        posts13 = []
        for postnumer in range(THIRTEEN):
            post1 = Post(
                text=POST_TEXT + "проверка пагинатора номер " + str(postnumer),
                author=cls.user,
                group=cls.group,
            )
            posts13.append(post1)
        Post.objects.bulk_create(posts13)

    def setUp(self):
        self.anotheruser_authorized = Client()
        self.anotheruser_authorized.force_login(self.anotheruser)

    def test_first_page_contains_ten_records_access(self):
        pages_name = (
            ("posts:index", None),
            ("posts:group_list", (self.group.slug,)),
            ("posts:profile", (self.user.username,)),
            ("posts:follow_index", None),
        )
        number_posts = (
            ("?page=1", settings.PAGINATION_ITEMS_PER_PAGE),
            ("?page=2", THIRTEEN - settings.PAGINATION_ITEMS_PER_PAGE),
        )
        for reverse_names, argument in pages_name:
            with self.subTest(reverse_names=reverse_names):
                url_with_arg = reverse(reverse_names, args=argument)
                for last_part_url, number in number_posts:
                    with self.subTest(last_part_url=last_part_url):
                        response = self.anotheruser_authorized.get(
                            url_with_arg + last_part_url
                        )
                        self.assertEqual(
                            len(response.context["page_obj"]), number
                        )


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.another_user = User.objects.create_user(username=ANOTHERUSER)
        cls.third_user = User.objects.create_user(username=THIRDUSER)
        cls.group = Group.objects.create(
            title=GROUP_TITLE, slug=GROUP_SLUG, description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=POST_TEXT + "проверка подписки нового пользователя",
            author=cls.user,
            group=cls.group,
            pub_date=PUB_DATE,
        )

    def setUp(self):
        self.anotheruser_client = Client()
        self.anotheruser_client.force_login(self.another_user)
        self.thirduser_client = Client()
        self.thirduser_client.force_login(self.third_user)

    def test_follow_access(self):
        """Авторизованный пользователь может подписываться на других
        пользователей"""
        Follow.objects.all().delete()
        count_follow = Follow.objects.count()
        self.anotheruser_client.get(
            reverse("posts:profile_follow", args=(self.third_user.username,))
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        follow_obj = Follow.objects.first()
        self.assertEqual(follow_obj.author, self.third_user)
        self.assertEqual(follow_obj.user, self.another_user)

    def test_unfollow_access(self):
        """Авторизованный пользователь может удалять других пользователей
        из подписок."""
        Follow.objects.all().delete()
        Follow.objects.create(user=self.another_user, author=self.third_user)
        count_follow = Follow.objects.count()
        self.anotheruser_client.get(
            reverse("posts:profile_unfollow", args=(self.third_user.username,))
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_newpost_forfollowers(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан"""
        Follow.objects.all().delete()
        response = self.anotheruser_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 0)
        self.anotheruser_client.get(
            reverse("posts:profile_follow", args=(self.user.username,))
        )
        response = self.anotheruser_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 1)

    def test_dont_follow_self(self):
        """Нельзя подписаться на самого себя"""
        count_follow = Follow.objects.count()
        self.anotheruser_client.get(
            reverse("posts:profile_follow", args=(self.another_user.username,))
        )
        self.assertEqual(Follow.objects.count(), count_follow)

    def test_not_follow_again(self):
        """Нельзя подписаться еще раз на того же пользователя"""
        Follow.objects.all().delete()
        self.anotheruser_client.get(
            reverse("posts:profile_follow", args=(self.user.username,))
        )
        count_follow = Follow.objects.count()
        self.assertEqual(Follow.objects.count(), count_follow)
        self.anotheruser_client.get(
            reverse("posts:profile_follow", args=(self.user.username,))
        )
        self.assertEqual(Follow.objects.count(), count_follow)
