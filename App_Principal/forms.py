from django import forms
from .models import Post, Comment
from .models import Profile

class PostForm(forms.ModelForm):

    class Meta:
        model = Post

        fields = [
            'content',
            'image',
        ]

        labels = {
            'content': 'Contenido',
            'image': 'Imagen',
        }

        help_texts = {
            'content': '',
            'image': '',
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment

        fields = ["content"]

        widgets = {
            "content": forms.TextInput(
                attrs={
                    "placeholder": "Escribe un comentario..."
                }
            )
        }

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            'display_name',
            'bio',
            'image',
            'location',
            'website',
        ]

        labels = {
            'display_name': 'Nombre de usuario',
            'bio': 'Biografía',
            'image': 'Imagen del perfil',
            'location': 'Ubicación',
            'website': 'Sitio web',
        }

        help_texts = {
            'display_name': '',
            'bio': '',
            'image': '',
            'location': '',
            'website': '',
        }

class SettingsForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "app_color",
            "profile_color",
            "posts_grid",
            "remember_session",
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Escribe un comentario...",
                    "rows": 3,
                }
            )
        }