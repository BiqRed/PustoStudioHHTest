from django.db import models
from django.utils import timezone

POINTS_ON_LOGIN = 10


class BoostType(models.Model):
    name = models.CharField(max_length=255)

    # other fields...

    def __str__(self):
        return self.name


class Boost(models.Model):
    class Method(models.TextChoices):
        LEVEL_COMPLETE = 'lc', 'Level Complete'
        MANUAL = 'm', 'Manual'

    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name="boosts")

    # other fields...

    boost_type = models.ForeignKey(BoostType, on_delete=models.CASCADE)
    method = models.CharField(max_length=2, choices=Method.choices, default=Method.MANUAL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.player} boost #{self.pk}'


class Player(models.Model):
    player_id = models.UUIDField(primary_key=True)

    # other fields...

    first_login = models.DateTimeField(null=True, blank=True)

    points = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def login(self) -> None:
        """Call this method when the player logs in to the game."""
        if self.first_login is None:
            self.first_login = timezone.now()

        self.points += POINTS_ON_LOGIN
        self.save()

    def add_boost(self, boost_type: BoostType, method: Boost.Method = Boost.Method.MANUAL) -> Boost:
        """
        Add a boost to the player.
        :param boost_type: BoostType object
        :param method: Boost method
        :return: Boost object
        """
        return Boost.objects.create(player=self, boost_type=boost_type, method=method)
