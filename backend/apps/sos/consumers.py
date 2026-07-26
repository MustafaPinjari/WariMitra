import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SOSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'sos_alerts'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def sos_alert(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
