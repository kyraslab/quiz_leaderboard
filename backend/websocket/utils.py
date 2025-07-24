import json
import logging
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class WebSocketNotifier:
    """
    Utility class for sending WebSocket notifications
    """
    
    def __init__(self):
        self.channel_layer = None
        self._initialize_channel_layer()
    
    def _initialize_channel_layer(self):
        """Initialize the channel layer"""
        try:
            from channels.layers import get_channel_layer
            self.channel_layer = get_channel_layer()
        except Exception as e:
            logger.warning(f"Could not initialize channel layer: {e}")
            self.channel_layer = None
    
    def _ensure_channel_layer(self):
        """Ensure channel layer is available"""
        if self.channel_layer is None:
            self._initialize_channel_layer()
        return self.channel_layer is not None
    
    def send_quiz_session_uploaded(self, quiz_session_data):
        """
        Send notification when a new quiz session is uploaded
        
        Args:
            quiz_session_data: Dictionary containing quiz session information
        """
        if not self._ensure_channel_layer():
            logger.warning("Channel layer not available, skipping WebSocket notification")
            return
            
        try:
            async_to_sync(self.channel_layer.group_send)(
                'leaderboard_general',
                {
                    'type': 'quiz_session_uploaded',
                    'data': {
                        'message': 'New quiz session uploaded',
                        'session_id': quiz_session_data.get('session_id'),
                        'user_id': quiz_session_data.get('user_id'),
                        'quiz_id': quiz_session_data.get('quiz_id'),
                        'bidang': quiz_session_data.get('bidang'),
                        'timestamp': quiz_session_data.get('timestamp')
                    }
                }
            )
            
            if quiz_session_data.get('quiz_id'):
                async_to_sync(self.channel_layer.group_send)(
                    f"leaderboard_quiz_{quiz_session_data['quiz_id']}",
                    {
                        'type': 'quiz_session_uploaded',
                        'data': {
                            'message': f"New session for quiz {quiz_session_data['quiz_id']}",
                            'session_id': quiz_session_data.get('session_id'),
                            'user_id': quiz_session_data.get('user_id'),
                            'score': quiz_session_data.get('score'),
                            'timestamp': quiz_session_data.get('timestamp')
                        }
                    }
                )
            
            logger.info(f"WebSocket notification sent for quiz session upload: {quiz_session_data.get('session_id')}")
            
        except Exception as e:
            logger.error(f"Failed to send quiz session upload notification: {e}")
    
    def send_leaderboard_updated(self, leaderboard_data):
        """
        Send notification when leaderboard is updated
        
        Args:
            leaderboard_data: Dictionary containing leaderboard update information
        """
        if not self._ensure_channel_layer():
            logger.warning("Channel layer not available, skipping WebSocket notification")
            return
            
        try:
            async_to_sync(self.channel_layer.group_send)(
                'leaderboard_general',
                {
                    'type': 'leaderboard_updated',
                    'data': {
                        'message': 'Leaderboard updated',
                        'affected_bidang': leaderboard_data.get('bidang'),
                        'affected_quiz_id': leaderboard_data.get('quiz_id'),
                        'timestamp': leaderboard_data.get('timestamp')
                    }
                }
            )
            
            logger.info(f"WebSocket notification sent for leaderboard update: {leaderboard_data.get('update_type')}")
            
        except Exception as e:
            logger.error(f"Failed to send leaderboard update notification: {e}")
    
    def send_quiz_leaderboard_updated(self, quiz_id, timestamp):
        """
        Send notification when quiz-specific leaderboard is updated
        
        Args:
            quiz_id: Quiz ID
            timestamp: Timestamp of the update
        """
        if not self._ensure_channel_layer():
            logger.warning("Channel layer not available, skipping WebSocket notification")
            return
            
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'leaderboard_quiz_{quiz_id}',
                {
                    'type': 'quiz_leaderboard_updated',
                    'data': {
                        'message': 'Quiz leaderboard updated',
                        'quiz_id': quiz_id,
                        'timestamp': timestamp
                    }
                }
            )
            
            logger.info(f"WebSocket notification sent for quiz leaderboard update: {quiz_id}")
            
        except Exception as e:
            logger.error(f"Failed to send quiz leaderboard update notification: {e}")

websocket_notifier = WebSocketNotifier()
