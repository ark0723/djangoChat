# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))


# version 1
'''
class ChatConsumer(WebsocketConsumer):
    """
    This is a synchronous WebSocket consumer that accepts all connections,
    receives messages from its client, and echos those messages back to the same client.
    For now it does not broadcast messages to other clients in the same room.
    """

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
'''


# version 2
'''
class ChatConsumer(WebsocketConsumer):
    """
    channel layer applied: multiple consumer object availabe
    When a user posts a message, a JavaScript function will transmit the message over WebSocket to a ChatConsumer.
    The ChatConsumer will receive that message and forward it to the group corresponding to the room name.
    Every ChatConsumer in the same group (and thus in the same room) will then receive the message
    from the group and forward it over WebSocket back to JavaScript, where it will be appended to the chat log.
    """

    def connect(self):
        # room_name을 받아서, group을 만든다
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group: 생성된 그룹을 채널레이어에 넣는다
        # async_to_sync: ChatConsumer is a synchronous WebsocketConsumer
        # but it is calling an asynchronous channel layer method
        # (All channel layer methods are asynchronous.)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        # connection 생성
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        # An event has a special 'type' key corresponding to the name of the method
        # that should be invoked on consumers that receive the event.
        # This translation is done by replacing . with _,
        # thus in this example, chat.message calls the chat_message method.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
'''
