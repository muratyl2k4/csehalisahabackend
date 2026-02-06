from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match, PlayerMatchStats
from players.models import Player

@receiver(post_save, sender=Match)
def create_initial_match_roster(sender, instance, created, **kwargs):
    """
    Maç ilk oluşturulduğunda, takımların mevcut oyuncularını
    otomatik olarak maç kadrosuna ekler.
    """
    if created:
        # Team 1 Players
        team1_players = Player.objects.filter(current_team=instance.team1)
        for player in team1_players:
            PlayerMatchStats.objects.create(
                match=instance,
                player=player,
                team=instance.team1,
                played=True  # Varsayılan olarak oynuyor işaretle, sonra değiştirilebilir
            )
            
        # Team 2 Players
        team2_players = Player.objects.filter(current_team=instance.team2)
        for player in team2_players:
            PlayerMatchStats.objects.create(
                match=instance,
                player=player,
                team=instance.team2,
                played=True
            )
