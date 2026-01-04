import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from webpush.models import PushInformation, SubscriptionInfo

print(f"Deleting {PushInformation.objects.count()} PushInformation records...")
PushInformation.objects.all().delete()

print(f"Deleting {SubscriptionInfo.objects.count()} SubscriptionInfo records...")
SubscriptionInfo.objects.all().delete()

print("All subscriptions cleared. Database is clean.")
