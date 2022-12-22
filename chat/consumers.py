import asyncio
from time import sleep
from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
from django.contrib.auth.models import AnonymousUser

class MySyncConsumer(SyncConsumer):
    def websocket_connect(self,event):
        print(self)
        self.send({
            'type':'websocket.accept'
        })
    
    def websocket_receive(self,event):
        print('Received',event)
        for i in range(1):
            self.send({
                'type':'websocket.send',
                'text':f"{i}"
            })
            sleep(0.1)
    
    def websocket_disconnect(self,event):
        raise StopConsumer()

class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        if not isinstance(self.scope['user'],AnonymousUser):
            await self.send({
                'type':'websocket.accept'
            })
            await self.send({
                'type':'websocket.send',
                'text':f"Hello {self.scope['user'].name}"
            })
    
    async def websocket_receive(self,event):
        print('Received',event)
        for i in range(10):
            await self.send({
                'type':'websocket.send',
                'text':f"{i}"
            })
            await asyncio.sleep(0.1)
    
    async def websocket_disconnect(self,event):
        raise StopConsumer()