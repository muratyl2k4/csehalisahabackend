from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from webpush import send_user_notification

@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if created:
        try:
            from webpush.models import PushInformation
            from pywebpush import webpush
            import json
            import sys

            # 1. Kullanıcının aboneliklerini bul
            push_infos = PushInformation.objects.filter(user=instance.recipient).select_related('subscription')
            
            if not push_infos.exists():
                return

            # 2. Payload Hazırla
            payload = json.dumps({
                "title": instance.title if instance.title else "Bildirim",
                "body": instance.message,
                "icon": "/logo1.png",
                "url": instance.related_link if instance.related_link else "/"
            })

            # 3. Her abonelik için gönder (Hardcoded Keys ile)
            for pi in push_infos:
                sub = pi.subscription
                try:
                    webpush(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {
                                "auth": sub.auth,
                                "p256dh": sub.p256dh
                            }
                        },
                        data=payload,
                        vapid_private_key="vokzWx36wRxAC1BWWVKskRwR1QzhxRGkvEixejFa1zI",
                        vapid_claims={"sub": "mailto:akdenizcselig@gmail.com"},
                        ttl=60
                    )
                    print(f"✅ Auto-Push Sent to {instance.recipient.username}", file=sys.stdout, flush=True)
                except Exception as inner_e:
                    print(f"🔴 Auto-Push Error: {inner_e}", file=sys.stdout, flush=True)
                    pass

        except Exception as e:
            print(f"🔴 Signal Error: {e}", file=sys.stdout, flush=True)
