from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )
        labels = {
            "text": "Текст записи",
            "group": "Группа",
            "image": "Изображение",
        }
        help_texts = {
            "text": "Текст вашей записи",
            "group": "Выберите группу",
            "image": "Выберите изображение",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст комментария",
        }
        help_texts = {
            "text": "Текст вашего комментария",

        }
