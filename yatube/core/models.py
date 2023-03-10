from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""

    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    text = models.TextField("Текст поста", help_text="Введите текст поста")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        abstract = True
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.text[:15]}... "
