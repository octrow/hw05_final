from django.test import TestCase

from ..models import Group, Post, User
from .const import (AUTHOR, GROUP_DESCRIPTION, GROUP_SLUG, GROUP_TITLE,
                    POST_TEXT)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(author=cls.user, text=POST_TEXT)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(PostModelTest.post), POST_TEXT[:15] + "... ")
        self.assertEqual(str(PostModelTest.group), GROUP_TITLE)

    def test_models_have_correct_verbose_names(self):
        """Проверяем, что модели имеют верное поле verbose_names."""
        self.assertEqual(
            Post._meta.get_field("text").verbose_name, "Текст поста"
        )
        self.assertEqual(
            Group._meta.get_field("title").verbose_name, "Имя группы"
        )

    def test_models_have_correct_help_texts(self):
        """Проверяем, что моделей имеет верное поле help_text."""
        self.assertEqual(
            Post._meta.get_field("text").help_text, "Введите текст поста"
        )
        self.assertEqual(Group._meta.get_field("title").help_text, "")

    def test_post_creation(self):
        """Проверяем, что модели создаются правильно."""
        self.assertEqual(PostModelTest.post.text, POST_TEXT)
        self.assertEqual(PostModelTest.post.author, PostModelTest.user)
        self.assertEqual(PostModelTest.group.title, GROUP_TITLE)
        self.assertEqual(PostModelTest.group.slug, GROUP_SLUG)
        self.assertEqual(PostModelTest.group.description, GROUP_DESCRIPTION)
        self.assertEqual(PostModelTest.user.username, AUTHOR)

    def test_group_creation(self):
        """Проверяем, что модель Group создается правильно."""
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(
            Group.objects.get(title="Тестовая группа").title, GROUP_TITLE
        )
        self.assertEqual(
            Group.objects.get(title="Тестовая группа").slug, GROUP_SLUG
        )
        self.assertEqual(
            Group.objects.get(title="Тестовая группа").description,
            GROUP_DESCRIPTION,
        )
