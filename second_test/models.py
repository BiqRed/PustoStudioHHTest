from threading import Thread

from django.db import models, IntegrityError
from django.utils import timezone

from .export import export_to_cvs


class Player(models.Model):
    player_id = models.CharField(max_length=100)

    def start_level(self, level: 'Level') -> 'PlayerLevel':
        """Call this method when the player starts the current level."""
        try:
            player_level = PlayerLevel.objects.create(player=self, level=level)
        except IntegrityError:
            player_level = PlayerLevel.objects.get(player=self, level=level)
        return player_level

    def complete_level(self, level: 'Level', score: int) -> 'PlayerLevel':
        """Call this method when the player completes the current level."""
        try:
            player_level = PlayerLevel.objects.get(player=self, level=level)
        except PlayerLevel.DoesNotExist:
            raise Exception(f'Player {self} has not started level {level}')

        player_level.is_completed = True
        player_level.completed = timezone.now()
        player_level.score = score
        player_level.save()

        # give the prize to the player
        player_level.give_prize()

        return player_level


class Prize(models.Model):
    title = models.CharField()


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)


class PlayerLevel(models.Model):
    class Meta:
        unique_together = ('player', 'level')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def give_prize(self) -> 'PlayerLevelPrize':
        """Receive the prize to the player for the current level."""
        try:
            player_level_prize = PlayerLevelPrize.objects.create(
                completed_level=self,
                prize=self.level.prize,
                received=timezone.now(),
            )
        except IntegrityError:
            raise Exception(f'Player {self.player} already received prize for level {self.level}')
        return player_level_prize

    @classmethod
    def export_to_cvs(cls):
        """Export data about user"""
        queryset = cls.objects.select_related('player', 'level', 'received_prize').iterator()

        # Run export in separate thread to not block the main thread
        Thread(target=export_to_cvs, args=(queryset,)).start()


class PlayerLevelPrize(models.Model):
    completed_level = models.OneToOneField(PlayerLevel, on_delete=models.CASCADE, related_name='received_prize')
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()
