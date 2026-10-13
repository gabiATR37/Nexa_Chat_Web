from datetime import date, datetime
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import views as auth_views
from .forms import PostForm, CommentForm, ProfileForm
from .models import Profile, Post, Like, Comment, Follow, Notification
from .forms import SettingsForm
from App_Principal.models import Profile


def index(request):
    return render(
        request,
        "App_Principal/index.html",
        {
            "now": datetime.now()
        }
    )


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)
            return redirect("home")

        messages.error(
            request,
            "Usuario o contraseña incorrectos."
        )

    return render(
        request,
        "App_Principal/login.html"
    )

    login(request, user)

    if profile.remember_session:
        request.session.set_expiry(1209600)
    else:
        request.session.set_expiry(0)


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        dni = request.POST.get("dni")
        birth_date = request.POST.get("birth_date")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "App_Principal/register.html",
                {
                    "error": "Ese nombre de usuario ya existe."
                }
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "App_Principal/register.html",
                {
                    "error": "Ese correo ya está registrado."
                }
            )

        if Profile.objects.filter(dni=dni).exists():
            return render(
                request,
                "App_Principal/register.html",
                {
                    "error": "Ese DNI ya está registrado."
                }
            )

        birth = date.fromisoformat(birth_date)

        today = date.today()

        age = (
            today.year
            - birth.year
            - (
                (today.month, today.day)
                < (birth.month, birth.day)
            )
        )

        if age < 16:
            return render(
                request,
                "App_Principal/register.html",
                {
                    "error": "Debes tener al menos 16 años."
                }
            )

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Crear perfil manualmente
        Profile.objects.create(
            user=user,
            dni=dni,
            birth_date=birth,
            display_name=username
        )

        messages.success(
            request,
            "Cuenta creada correctamente."
        )

        return redirect("login")

    return render(
        request,
        "App_Principal/register.html"
    )


@login_required
def home(request):

    following = Follow.objects.filter(
        follower=request.user
    ).values_list(
        "following",
        flat=True
    )

    posts = Post.objects.filter(
        Q(author=request.user) |
        Q(author__in=following)
    ).order_by("-created_at")

    comment_form = CommentForm()

    return render(
        request,
        "App_Principal/home.html",
        {
            "posts": posts,
            "comment_form": comment_form,
        }
    )

@login_required
def create_post(request):

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            post = form.save(commit=False)

            post.author = request.user

            post.save()

            messages.success(
                request,
                "Publicación creada correctamente."
            )

            return redirect("home")

    else:

        form = PostForm()

    return render(
        request,
        "App_Principal/create_post.html",
        {
            "form": form
        }
    )

@login_required
def toggle_like(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )

    like = Like.objects.filter(
        user=request.user,
        post=post
    )

    if like.exists():

        like.delete()

    else:

        Like.objects.create(
            user=request.user,
            post=post
        )

        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                sender=request.user,
                notification_type="like",
                post=post,
            )

    return redirect(request.META.get("HTTP_REFERER", "home"))



@login_required
def add_comment(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.author = request.user

            comment.post = post

            comment.save()

    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        author=request.user
    )

    if request.method == "POST":

        form = CommentForm(
            request.POST,
            instance=comment
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Comentario actualizado correctamente."
            )

            return redirect(
                request.META.get("HTTP_REFERER", "home")
            )

    else:

        form = CommentForm(
            instance=comment
        )

    return render(
        request,
        "App_Principal/edit_comment.html",
        {
            "form": form,
            "comment": comment,
        }
    )


@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        author=request.user
    )

    if request.method == "POST":

        comment.delete()

        messages.success(
            request,
            "Comentario eliminado correctamente."
        )

        return redirect(
            request.META.get("HTTP_REFERER", "home")
        )

    return render(
        request,
        "App_Principal/delete_comment.html",
        {
            "comment": comment,
        }
    )

@login_required
def profile(request, username):

    profile_user = get_object_or_404(
        User,
        username=username
    )

    posts = Post.objects.filter(
        author=profile_user
    ).order_by("-created_at")

    posts_count = posts.count()

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()

    return render(
        request,
        "App_Principal/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile_user.profile,
            "posts": posts,
            "posts_count": posts_count,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
        }
    )

def logout_view(request):

    logout(request)

    return redirect("login")




@login_required
def toggle_follow(request, username):

    user_to_follow = get_object_or_404(
        User,
        username=username
    )

    # Evitar seguirse a sí mismo
    if user_to_follow == request.user:
        return redirect(
            "profile",
            username=username
        )

    follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    )

    if follow.exists():

        follow.delete()

    else:

        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect(
        "profile",
        username=username
    )

@login_required
def edit_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user
    )

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            form.save()
            return redirect("profile", username=request.user.username)

    else:

        form = PostForm(instance=post)

    return render(
        request,
        "App_Principal/edit_post.html",
        {
            "form": form,
            "post": post,
        }
    )

@login_required
def delete_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )

    if post.author != request.user:
        return redirect("home")

    if request.method == "POST":

        post.delete()

        return redirect(
            "profile",
            username=request.user.username
        )

    return render(
        request,
        "App_Principal/delete_post.html",
        {
            "post": post,
        }
    )

@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Perfil actualizado correctamente."
            )

            return redirect(
                "profile",
                username=request.user.username
            )

        print(form.errors)

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "App_Principal/edit_profile.html",
        {
            "form": form
        }
    )

@login_required
def explore(request):

    query = request.GET.get("q", "")

    # Publicaciones recientes excepto las del usuario actual
    posts = Post.objects.exclude(
        author=request.user
    ).order_by("-created_at")

    # Usuarios encontrados
    users = Profile.objects.none()

    if query:
        users = Profile.objects.filter(
            Q(user__username__icontains=query) |
            Q(display_name__icontains=query)
        ).exclude(user=request.user)

    context = {
        "posts": posts,
        "users": users,
        "query": query,
    }

    return render(
        request,
        "App_Principal/explore.html",
        context
    )

@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "App_Principal/notifications.html",
        {
            "notifications": notifications
        }
    )

@login_required
def settings_view(request):

    profile = request.user.profile

    if request.method == "POST":

        form = SettingsForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            if profile.remember_session:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

            messages.success(
                request,
                "Configuración guardada."
            )

            return redirect("settings")

    else:

        form = SettingsForm(
            instance=profile
        )

    return render(
        request,
        "App_Principal/settings.html",
        {
            "form": form
        }
    )

@login_required
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    comments = post.comments.select_related(
        "author",
        "author__profile"
    ).order_by("-created_at")

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

            return redirect("post_comments", post_id=post.id)
    else:
        form = CommentForm()

    return render(
        request,
        "App_Principal/comentarios_post.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
        },
    )