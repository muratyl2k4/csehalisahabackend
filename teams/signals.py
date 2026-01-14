from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TransferRequest
from notifications.models import Notification

@receiver(post_save, sender=TransferRequest)
def notify_on_transfer_request_update(sender, instance, created, **kwargs):
    """
    Sends notification when transfer request is created or updated
    """
    
    # New Request -> Notify Captain
    if created:
        team = instance.team
        player = instance.player
        
        # Ensure team has a captain
        if team.captain and team.captain.user:
            Notification.objects.create(
                recipient=team.captain.user,
                message=f"{player.name}, {team.name} takımına katılmak istiyor.",
                notification_type='TEAM_REQUEST',
                related_link=f"/teams/{team.id}/requests" # Frontend route
            )
            
    # Request Status Changed (Accepted/Rejected) -> Notify Player
    else:
        
        if instance.status in ['ACCEPTED', 'REJECTED']:
            player = instance.player
            team = instance.team
            status_text = "kabul edildi" if instance.status == 'ACCEPTED' else "reddedildi"
            
            if player.user:
                Notification.objects.create(
                    recipient=player.user,
                    message=f"{team.name} takımına katılım isteğiniz {status_text}.",
                    notification_type='TEAM_RESPONSE',
                    related_link=f"/teams/{team.id}"
                )
