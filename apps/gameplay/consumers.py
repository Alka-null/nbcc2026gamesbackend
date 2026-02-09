import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Sum, F, Q
from .models import Challenge
from .quiz_stats import QuizStat


class LeaderboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time leaderboard updates.
    Sends updates only when rankings change.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_leaderboard = []
        self.update_task = None
        self.challenge_id = None
        
    async def connect(self):
        """Accept WebSocket connection and start background task."""
        await self.accept()
        
        # Start background task to periodically check for leaderboard updates
        self.update_task = asyncio.create_task(self.send_leaderboard_updates())
        
    async def disconnect(self, close_code):
        """Cancel background task on disconnect."""
        if self.update_task:
            self.update_task.cancel()
            
    async def receive(self, text_data):
        """Handle messages from WebSocket (optional for future use)."""
        pass
    
    @database_sync_to_async
    def get_leaderboard_data(self):
        """
        Fetch and calculate leaderboard rankings for the active challenge.
        Rankings based on:
        1. Number of correct answers (DESC)
        2. Total time taken (ASC) - faster is better
        """
        # Get the latest active challenge
        challenge = Challenge.objects.filter(is_active=True).order_by('-started_at').first()
        
        if not challenge:
            return None, []
        
        User = get_user_model()
        
        # Get all users who have answered questions in this challenge
        user_stats = QuizStat.objects.filter(
            challenge=challenge
        ).values('user').distinct()
        
        leaderboard = []
        
        for user_stat in user_stats:
            user_id = user_stat['user']
            user = User.objects.filter(id=user_id).first()
            
            if not user:
                continue
            
            # Get stats for this user in the current challenge
            stats = QuizStat.objects.filter(
                user_id=user_id,
                challenge=challenge
            )
            
            total_answered = stats.count()
            total_correct = stats.filter(is_correct=True).count()
            total_time = stats.aggregate(total=Sum('time_taken'))['total'] or 0.0
            
            leaderboard.append({
                'user_id': user.id,
                'unique_code': user.unique_code,
                'name': user.name,
                'total_answered': total_answered,
                'total_correct': total_correct,
                'total_time': round(total_time, 2),
            })
        
        # Sort by total_correct (DESC), then by total_time (ASC)
        leaderboard.sort(key=lambda x: (-x['total_correct'], x['total_time']))
        
        # Add rank to each entry
        for idx, entry in enumerate(leaderboard, start=1):
            entry['rank'] = idx
            
        return challenge.id, leaderboard
    
    def has_leaderboard_changed(self, new_leaderboard):
        """
        Compare new leaderboard with previous to detect ranking changes.
        Returns True if any rank position has changed.
        """
        if len(new_leaderboard) != len(self.previous_leaderboard):
            return True
        
        # Create rank mapping for comparison
        new_ranks = {entry['user_id']: entry['rank'] for entry in new_leaderboard}
        old_ranks = {entry['user_id']: entry['rank'] for entry in self.previous_leaderboard}
        
        # Check if any ranks have changed
        for user_id, new_rank in new_ranks.items():
            if old_ranks.get(user_id) != new_rank:
                return True
                
        return False
    
    async def send_leaderboard_updates(self):
        """
        Background task that periodically fetches leaderboard and sends updates.
        Only sends when rankings change to optimize network usage.
        """
        try:
            while True:
                challenge_id, leaderboard = await self.get_leaderboard_data()
                
                if challenge_id is None:
                    # No active challenge, send empty state
                    await self.send(text_data=json.dumps({
                        'type': 'leaderboard_update',
                        'challenge_id': None,
                        'leaderboard': [],
                        'message': 'No active challenge'
                    }))
                    await asyncio.sleep(5)  # Check every 5 seconds
                    continue
                
                # Check if challenge has changed
                if self.challenge_id != challenge_id:
                    self.challenge_id = challenge_id
                    self.previous_leaderboard = []
                
                # Only send update if rankings have changed
                if self.has_leaderboard_changed(leaderboard):
                    await self.send(text_data=json.dumps({
                        'type': 'leaderboard_update',
                        'challenge_id': challenge_id,
                        'leaderboard': leaderboard,
                        'timestamp': asyncio.get_event_loop().time()
                    }))
                    
                    self.previous_leaderboard = leaderboard
                
                # Poll every 2 seconds for optimal real-time updates
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            # Task cancelled on disconnect
            pass
        except Exception as e:
            # Log error and close connection
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
            await self.close()
