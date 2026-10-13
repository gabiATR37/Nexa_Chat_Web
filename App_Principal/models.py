from django.db import models
from django.contrib.auth.models import User


# ==========================
# PERFIL
# ==========================

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    display_name = models.CharField(
        max_length=50,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="profiles/",
        default="profiles/default.png"
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    dni = models.CharField(
        max_length=20,
        unique=True
    )

    birth_date = models.DateField(
        blank=True,
        null=True
    )

    APP_COLORS = [
        ("blue", "Azul"),
        ("purple", "Violeta"),
        ("green", "Verde"),
        ("red", "Rojo"),
        ("dark", "Oscuro"),
    ]

    GRID_OPTIONS = [
        (3, "3 columnas"),
        (4, "4 columnas"),
        (5, "5 columnas"),
    ]

    app_color = models.CharField(
        max_length=20,
        choices=APP_COLORS,
        default="blue"
    )

    profile_color = models.CharField(
        max_length=20,
        choices=APP_COLORS,
        default="blue"
    )

    posts_grid = models.IntegerField(
        choices=GRID_OPTIONS,
        default=3
    )

    remember_session = models.BooleanField(
        default=True
    )

    

# ==========================
# PUBLICACIONES
# ==========================

class Post(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    content = models.TextField(
        max_length=500,
        blank=True
    )

    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} - {self.created_at}"


# ==========================
# LIKES
# ==========================

class Like(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "user",
            "post"
        )

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.id}"

# ==========================
# SEGUIDORES
# ==========================

class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "follower",
            "following"
        )

    def __str__(self):
        return f"{self.follower.username} sigue a {self.following.username}"
    
# ==========================
# NOTIFICACIONES
# ==========================

class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ("like", "Like"),
        ("comment", "Comentario"),
        ("follow", "Seguidor"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender} -> {self.user} ({self.notification_type})"


primary_color = models.CharField(max_length=10, default="#2563eb")

profile_color = models.CharField(max_length=10, default="#2563eb")

banner_color = models.CharField(max_length=10, default="#1e3a8a")

posts_layout = models.CharField(
    max_length=20,
    default="list"
)

remember_session = models.BooleanField(default=True)

# ==========================
# COMENTARIOS
# ==========================

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} - {self.post.id}"