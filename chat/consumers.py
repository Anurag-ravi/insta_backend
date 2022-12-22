import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
    
class ChatConsumer(AsyncWebsocketConsumer):
    room_name = ""
    async def connect(self):
        if not self.scope['user'].is_anonymous():
            profile = self.scope['user']
            self.room_name = str(profile.id)
            # Join room group
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            await self.send(text_data=f"{profile.name} your room name is {self.room_name} channel_name is {self.channel_name}")
    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
        except:
            return
        print('Received',text_data_json)
        for i in range(10):
            await self.send(text_data=json.dumps({
                'text':f"{i}"
            }))
            await asyncio.sleep(0.1)
            
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
    