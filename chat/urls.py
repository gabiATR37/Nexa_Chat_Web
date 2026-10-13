from django.urls import path
from . import views

urlpatterns = [
    path("", views.chats, name="chats"),

    path(
        "nuevo/<str:username>/",
        views.nuevo_chat,
        name="nuevo_chat",
    ),

    path(
        "<int:conversation_id>/",
        views.conversacion,
        name="conversacion",
    ),

    path(
        "<int:conversation_id>/upload/",
        views.upload_file,
        name="upload_file",
    ),
]