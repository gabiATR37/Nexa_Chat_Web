from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # Página principal
    path(
        '',
        views.index,
        name='index'
    ),

    # Autenticación
    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # Home
    path(
        'home/',
        views.home,
        name='home'
    ),

    # Editar perfil
    path(
        'profile/edit/',
        views.edit_profile,
        name='edit_profile'
    ),

    # Perfil
    path(
        'profile/<str:username>/',
        views.profile,
        name='profile'
    ),

    # Publicaciones
    path(
        "post/create/",
        views.create_post,
        name="create_post"
    ),

    # Editar publicación
    path(
        "post/<int:post_id>/edit/",
        views.edit_post,
        name="edit_post"
    ),

    # Eliminar publicación
    path(
        "post/<int:post_id>/delete/",
        views.delete_post,
        name="delete_post"
    ),

    path(
        "post/<int:post_id>/like/",
        views.toggle_like,
        name="toggle_like"
    ),

    path(
        "post/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment"
    ),

    path(
        "explore/",
        views.explore,
        name="explore"
    ),

    path(
        "follow/<str:username>/",
        views.toggle_follow,
        name="toggle_follow"
    ),
    

    path(
        "notifications/",
        views.notifications,
        name="notifications"
    ),

    path("settings/",
        views.settings_view,
        name="settings"
    ),

    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="App_Principal/change_password.html",
            success_url="/settings/"
        ),
        name="change_password",
    ),

    path(
        "post/<int:post_id>/comentarios/",
        views.post_comments,
        name="post_comments",
    ),
    

]