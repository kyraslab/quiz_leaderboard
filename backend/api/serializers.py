from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Quiz, QuizSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class QuizSerializer(serializers.ModelSerializer):
    bidang_name = serializers.CharField(source='get_bidang_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'bidang', 'bidang_name', 'start_date', 'end_date', 'is_active', 'status']

class QuizSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    quiz_id = serializers.IntegerField()
    duration = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = QuizSession
        fields = [
            'id', 'username', 'user_id', 'quiz_id', 
            'score', 'duration', 'user_start', 'user_end'
        ]
    
    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        return value
    
    def validate_quiz_id(self, value):
        try:
            quiz = Quiz.objects.get(id=value)
            now = timezone.now()
            if now < quiz.start_date:
                raise serializers.ValidationError("Quiz has not started yet")
            if now > quiz.end_date:
                raise serializers.ValidationError("Quiz has already ended")
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist")
        return value
    
    def validate(self, data):
        if data.get('user_start') and data.get('user_end'):
            if data['user_start'] >= data['user_end']:
                raise serializers.ValidationError("End time must be after start time")
        return data


class QuizSessionCreateSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = QuizSession
        fields = ['user', 'quiz', 'score', 'duration', 'user_start', 'user_end']
    
    def validate_quiz(self, value):
        now = timezone.now()
        if now < value.start_date:
            raise serializers.ValidationError("Quiz has not started yet")
        if now > value.end_date:
            raise serializers.ValidationError("Quiz has already ended")
        return value
    
    def validate(self, data):
        if data.get('user_start') and data.get('user_end'):
            if data['user_start'] >= data['user_end']:
                raise serializers.ValidationError("End time must be after start time")
        
        user = data.get('user')
        quiz = data.get('quiz')
        if user and quiz:
            existing_session = QuizSession.objects.filter(user=user, quiz=quiz).first()
            if existing_session:
                raise serializers.ValidationError("User has already attempted this quiz. Only one attempt per quiz is allowed.")
        
        if data.get('quiz'):
            quiz = data['quiz']
            user_start = data.get('user_start')
            user_end = data.get('user_end')
            
            if user_start and user_start < quiz.start_date:
                raise serializers.ValidationError("Session start time cannot be before quiz start time")
            if user_end and user_end > quiz.end_date:
                raise serializers.ValidationError("Session end time cannot be after quiz end time")
        
        return data
    
    def create(self, validated_data):
        if validated_data.get('user_start') and validated_data.get('user_end'):
            time_diff = validated_data['user_end'] - validated_data['user_start']
            validated_data['duration'] = int(time_diff.total_seconds())
        
        return super().create(validated_data)


class SubjectLeaderboardSerializer(serializers.Serializer):
    """Serializer for subject-based leaderboard (aggregated scores per user per subject)"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_score = serializers.IntegerField()
    quiz_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_duration = serializers.IntegerField()
    average_duration = serializers.FloatField()


class QuizLeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for quiz session leaderboard (individual quiz performances)"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = QuizSession
        fields = [
            'id', 'username', 'user_id', 'score', 'duration', 'user_start', 'user_end'
        ]
