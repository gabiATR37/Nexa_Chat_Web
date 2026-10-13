from django.urls import path
from . import views

urlpatterns = [
    path("", views.music_home, name="music_home"),
]