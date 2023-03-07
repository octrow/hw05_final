from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image" 
        )
        labels = {
            "text": "Текст записи",
            "group": "Группа",
        }
        help_texts = {
            "text": "Текст вашей записи",
            "group": "Выберите группу",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
