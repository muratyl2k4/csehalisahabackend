from django.core.management.base import BaseCommand
from matches.services import RatingService
from players.models import Player

class Command(BaseCommand):
    help = 'Recalculates all player ratings to initialize running totals'

    def handle(self, *args, **kwargs):
        players = Player.objects.all()
        count = players.count()
        self.stdout.write(f"Found {count} players. Starting recalculation...")

        for player in players:
            try:
                # Calling with new_rating=None forces a full recalc from history
                RatingService.update_player_overall(player.id, new_rating=None)
                self.stdout.write(self.style.SUCCESS(f"Updated {player.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed {player.name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully recalculated all ratings."))
