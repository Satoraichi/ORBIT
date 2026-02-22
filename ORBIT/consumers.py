# ORBIT/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Event, DirectorInstruction

class InstructionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.event_slug = self.scope['url_route']['kwargs']['event_slug']
        self.room_group_name = f'instruction_{self.event_slug}'

        # イベントごとのグループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketからデータを受信したとき
    async def receive(self, text_data):
        data = json.loads(text_data)
        action_type = data['action_type']

        # DBに保存（非同期処理の中で同期DB操作を行うためのデコレータを使用）
        await self.save_instruction(action_type)

        # グループ全員にメッセージを送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'instruction_message',
                'action_type': action_type
            }
        )

    # グループメッセージを受信したとき
    async def instruction_message(self, event):
        action_type = event['action_type']

        # ブラウザに送信
        await self.send(text_data=json.dumps({
            'action_type': action_type
        }))

    @database_sync_to_async
    def save_instruction(self, action_type):
        event = Event.objects.get(slug=self.event_slug)
        return DirectorInstruction.objects.create(event=event, action_type=action_type)