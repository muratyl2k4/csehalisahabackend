from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from webpush import send_user_notification

@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if created:
        try:
            # Kullanıcının bildirim mesajını ve varsa linkini al
            payload = {
                "title": instance.title,
                "body": instance.message,
                "icon": "/logo1.png",  # Frontend'deki logo yolu
                "url": instance.related_link if instance.related_link else "/"
            }
            
            # Webpush kütüphanesini kullanarak bildirimi gönder
            send_user_notification(
                user=instance.recipient,
                payload=payload,
                ttl=1000
            )
        except Exception as e:
            # Bildirim gönderilemezse logla ama sistemi durdurma
            print(f"Push notification error: {e}")
