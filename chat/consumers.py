import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print(f"WebSocket conectado al grupo {self.room_group_name}")

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print(f"WebSocket desconectado del grupo {self.room_group_name}")

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = data.get("message", "").strip()

        if not message:
            return

        await self.save_message(message)

        user_data = await self.get_user_data()

        print("Enviando al grupo:", message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": user_data["username"],
                "display_name": user_data["display_name"],
                "image": user_data["image"],
            }
        )

    async def chat_message(self, event):

        print("chat_message ejecutado:", event)

        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "username": event["username"],
                    "display_name": event["display_name"],
                    "image": event["image"],
                }
            )
        )

    async def chat_file(self, event):

        print("chat_file ejecutado")

        await self.send(
            text_data=json.dumps(
                {
                    "username": event["username"],
                    "display_name": event["display_name"],
                    "image": event["image"],
                    "message": event["message"],
                    "image_file": event["image_file"],
                    "video_file": event["video_file"],
                    "document_file": event["document_file"],
                    "audio_file": event["audio_file"],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, text):

        conversation = Conversation.objects.get(
            id=self.room_name,
            participants=self.user,
        )

        Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=text,
        )

    @database_sync_to_async
    def get_user_data(self):

        user = User.objects.select_related(
            "profile"
        ).get(id=self.user.id)

        return {
            "username": user.username,
            "display_name": user.profile.display_name or user.username,
            "image": user.profile.image.url if user.profile.image else "",
        }