from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(
        User,
        related_name="conversations"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Chat {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Mensaje de texto
    content = models.TextField(
        blank=True
    )

    # Imagen
    image = models.ImageField(
        upload_to="chat/images/",
        blank=True,
        null=True
    )

    # Video
    video = models.FileField(
        upload_to="chat/videos/",
        blank=True,
        null=True
    )

    # Documento
    document = models.FileField(
        upload_to="chat/documents/",
        blank=True,
        null=True
    )

    # Audio
    audio = models.FileField(
        upload_to="chat/audios/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.content:
            return f"{self.sender.username}: {self.content[:30]}"
        elif self.image:
            return f"{self.sender.username} envió una imagen"
        elif self.video:
            return f"{self.sender.username} envió un video"
        elif self.document:
            return f"{self.sender.username} envió un documento"
        elif self.audio:
            return f"{self.sender.username} envió un audio"
        return f"Mensaje {self.id}"