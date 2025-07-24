import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)


class LeaderboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time leaderboard notifications.
    
    Supports:
    - Quiz session upload notifications
    - Leaderboard update notifications  
    - Subject-specific and quiz-specific channels
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        token = self.scope['query_string'].decode().split('token=')[-1] if 'token=' in self.scope['query_string'].decode() else None
        
        if token:
            try:
                access_token = AccessToken(token)
                self.user = await self.get_user(access_token['user_id'])
                if not self.user:
                    await self.close()
                    return
            except (InvalidToken, TokenError, KeyError):
                logger.warning("Invalid token provided for WebSocket connection")
                await self.close()
                return
        else:
            self.user = None
        
        self.general_group_name = 'leaderboard_general'
        await self.channel_layer.group_add(
            self.general_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}, user: {self.user}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.general_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}, code: {close_code}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'subscribe_quiz':
                await self.subscribe_to_quiz(data.get('quiz_id'))
            elif message_type == 'unsubscribe_quiz':
                await self.unsubscribe_from_quiz(data.get('quiz_id'))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def subscribe_to_quiz(self, quiz_id):
        """Subscribe to quiz-specific leaderboard updates"""
        if quiz_id:
            group_name = f'leaderboard_quiz_{quiz_id}'
            await self.channel_layer.group_add(group_name, self.channel_name)
            await self.send(text_data=json.dumps({
                'type': 'subscription_confirmed',
                'quiz_id': quiz_id,
                'message': f'Subscribed to quiz {quiz_id} leaderboard updates'
            }))
    
    async def unsubscribe_from_quiz(self, quiz_id):
        """Unsubscribe from quiz-specific leaderboard updates"""
        if quiz_id:
            group_name = f'leaderboard_quiz_{quiz_id}'
            await self.channel_layer.group_discard(group_name, self.channel_name)
            await self.send(text_data=json.dumps({
                'type': 'unsubscription_confirmed',
                'quiz_id': quiz_id,
                'message': f'Unsubscribed from quiz {quiz_id} leaderboard updates'
            }))
    
    async def quiz_session_uploaded(self, event):
        """Handle quiz session upload notification"""
        await self.send(text_data=json.dumps({
            'type': 'quiz_session_uploaded',
            'data': event['data']
        }))
    
    async def leaderboard_updated(self, event):
        """Handle leaderboard update notification"""
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_updated',
            'data': event['data']
        }))
    
    async def quiz_leaderboard_updated(self, event):
        """Handle quiz leaderboard update notification"""
        await self.send(text_data=json.dumps({
            'type': 'quiz_leaderboard_updated',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
