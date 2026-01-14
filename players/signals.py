from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player

@receiver(post_save, sender=User)
def sync_user_to_player(sender, instance, **kwargs):
    """
    User (Hesap) güncellendiğinde, bağlı Player (Oyuncu) profilini güncelle.
    """
    if hasattr(instance, 'player_profile'):
        player = instance.player_profile
        
        # User isminin Player ismine yansıması
        full_name = instance.get_full_name()
        if full_name and player.name != full_name:
            player.name = full_name
            player.save(update_fields=['name'])
