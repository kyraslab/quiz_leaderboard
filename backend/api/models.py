from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bidang(models.TextChoices):
    AST = 'AST', 'Astronomi'
    BIO = 'BIO', 'Biologi'
    EKO = 'EKO', 'Ekonomi'
    FIS = 'FIS', 'Fisika'
    GEO = 'GEO', 'Geografi'
    INF = 'INF', 'Informatika'
    KBM = 'KBM', 'Kebumian'
    KIM = 'KIM', 'Kimia'
    MAT = 'MAT', 'Matematika'

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    bidang = models.CharField(max_length=3, choices=Bidang.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @property
    def is_active(self):
        """Check if the quiz is currently active"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    score = models.IntegerField()
    duration = models.IntegerField(help_text="duration in seconds")
    user_start = models.DateTimeField()
    user_end = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'quiz')

    def save(self, *args, **kwargs):
        if self.user_start and self.user_end:
            time_diff = self.user_end - self.user_start
            self.duration = int(time_diff.total_seconds())
        super().save(*args, **kwargs)
        super().save(*args, **kwargs)
