import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from customer.models import Customer
from .models import ChatRoom, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message = data["message"]

        await self.save_message(message)

        sender = await self.get_sender()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": sender,
                "message": message,
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "sender": event["sender"],
            "message": event["message"],
        }))

    @database_sync_to_async
    def save_message(self, message):

        room = ChatRoom.objects.get(id=self.room_id)

        user = self.scope["user"]
        superuser = self.scope.get("superuser")

        print("=" * 60)
        print("User:", user)
        print("Authenticated:", user.is_authenticated)
        print("Superuser:", superuser)
        print("Type:", type(superuser))
        print("ID:", getattr(superuser, "id", None))
        print("=" * 60)

        if superuser:
            ChatMessage.objects.create(
                room=room,
                sender="superuser",
                superuser=superuser,
                message=message
            )

        elif user.is_authenticated:
            customer = Customer.objects.get(user=user)

            ChatMessage.objects.create(
                room=room,
                sender="customer",
                customer=customer,
                message=message
            )
    @database_sync_to_async
    def get_sender(self):

        if self.scope["user"].is_authenticated:
            return "customer"

        return "superuser"