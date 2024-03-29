from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Имя группы", max_length=200)
    slug = models.SlugField("Slug группы", unique=True)
    description = models.TextField("Описание группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        if not self.title:
            return "Группа без названия"
        return self.title


class Post(CreatedModel):
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Группа",
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta(CreatedModel.Meta):
        verbose_name = ("Пост",)
        verbose_name_plural = "Посты"
        default_related_name = "posts"


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Пост",
    )

    class Meta(CreatedModel.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = "comments"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.CheckConstraint(
                check=models.Q(user=models.F("user")),
                name="нельзя подписаться на себя",
            ),
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            ),
        ]

    def __str__(self):
        return f"{self.user} подписался на {self.author}"
