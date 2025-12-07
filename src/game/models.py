from django.db import models
import uuid

class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    current_phase = models.IntegerField(default=1)

    def __str__(self):
        return f"Player {self.id}"

class GameLog(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    user_move = models.CharField(max_length=1)  # "R", "P", "S"
    ai_move = models.CharField(max_length=1)    # "R", "P", "S"
    result = models.CharField(max_length=10)    # "win", "lose", "draw"
    strategy_used = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GameLog {self.id} for {self.player}"
