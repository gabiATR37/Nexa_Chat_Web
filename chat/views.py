from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Conversation, Message
from django.db.models import Q


@login_required
def chats(request):
    buscar = request.GET.get("q", "").strip()

    conversaciones = Conversation.objects.filter(
        participants=request.user
    )

    usuarios = []

    if buscar:
        usuarios = User.objects.filter(
            Q(username__icontains=buscar) |
            Q(profile__display_name__icontains=buscar)
        ).exclude(
            id=request.user.id
        )[:1]

    return render(request, "chat/chats.html", {
        "conversations": conversaciones,
        "usuarios": usuarios,
        "buscar": buscar,
    })

@login_required
def nuevo_chat(request, username):

    otro_usuario = get_object_or_404(
        User,
        username=username
    )

    if otro_usuario == request.user:
        return redirect("chats")

    conversaciones = Conversation.objects.filter(
        participants=request.user
    )

    for conversacion in conversaciones:

        participantes = conversacion.participants.all()

        if (
            participantes.count() == 2
            and otro_usuario in participantes
        ):
            return redirect(
                "conversacion",
                conversation_id=conversacion.id
            )

    conversacion = Conversation.objects.create()

    conversacion.participants.add(
        request.user,
        otro_usuario
    )

    return redirect(
        "conversacion",
        conversation_id=conversacion.id
    )


@login_required
def conversacion(request, conversation_id):

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user,
    )

    conversations = (
        Conversation.objects
        .filter(participants=request.user)
        .prefetch_related("participants")
        .order_by("-created_at")
    )

    messages = (
        conversation.messages
        .select_related("sender", "sender__profile")
        .order_by("created_at")
    )

    return render(
        request,
        "chat/conversacion.html",
        {
            "conversation": conversation,
            "messages": messages,
            "conversations": conversations,
        },
    )


@login_required
def upload_file(request, conversation_id):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "error": "Método no permitido"
            },
            status=405
        )

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    image = request.FILES.get("image")
    video = request.FILES.get("video")
    document = request.FILES.get("document")
    audio = request.FILES.get("audio")

    if not any([image, video, document, audio]):
        return JsonResponse(
            {
                "success": False,
                "error": "No se recibió ningún archivo"
            },
            status=400
        )

    print("========== ARCHIVOS RECIBIDOS ==========")
    print("Imagen:", image)
    print("Video:", video)
    print("Documento:", document)
    print("Audio:", audio)

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=request.POST.get("content", ""),
        image=image,
        video=video,
        document=document,
        audio=audio,
    )

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"chat_{conversation.id}",
        {
            "type": "chat_file",
            "username": request.user.username,
            "display_name": request.user.profile.display_name or request.user.username,
            "image": request.user.profile.image.url if request.user.profile.image else "",
            "image_file": message.image.url if message.image else None,
            "video_file": message.video.url if message.video else None,
            "document_file": message.document.url if message.document else None,
            "audio_file": message.audio.url if message.audio else None,
            "message": message.content,
        }
    )

    print("========== ARCHIVOS GUARDADOS ==========")
    print("Imagen:", message.image)
    print("Video:", message.video)
    print("Documento:", message.document)
    print("Audio:", message.audio)

    print("========== URLS ==========")
    print("Imagen:", message.image.url if message.image else None)
    print("Video:", message.video.url if message.video else None)
    print("Documento:", message.document.url if message.document else None)
    print("Audio:", message.audio.url if message.audio else None)

    return JsonResponse(
        {
            "success": True,
            "message_id": message.id,
            "image": message.image.url if message.image else None,
            "video": message.video.url if message.video else None,
            "document": message.document.url if message.document else None,
            "audio": message.audio.url if message.audio else None,
        }
    )