import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GPSTelemetryConsumer(AsyncWebsocketConsumer):
    """
    Django Channels WebSocket Consumer:
    Handles live GPS telemetry streaming for police patrols, ambulances, water tankers, and emergency responders.
    """
    async def connect(self):
        self.room_group_name = 'wari_telemetry_live'

        # Join live telemetry channel group
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

    async def receive(self, text_data):
        """
        Receive location update payload from hardware/mobile transponder and broadcast to all connected clients.
        """
        try:
            data = json.loads(text_data)

            # Broadcast GPS location update to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'gps_location_update',
                    'data': data
                }
            )
        except Exception as e:
            pass

    async def gps_location_update(self, event):
        """
        Send location update down to WebSocket client.
        """
        await self.send(text_data=json.dumps(event['data']))
