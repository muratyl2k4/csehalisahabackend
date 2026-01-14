import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

pub = settings.WEBPUSH_SETTINGS.get('VAPID_PUBLIC_KEY')
priv = settings.WEBPUSH_SETTINGS.get('VAPID_PRIVATE_KEY')

print("\n--- BACKEND KEYS (Serverda Yüklü Olanlar) ---")
print(f"Public:  {pub}")
print(f"Private: {priv}")
print("-----------------------------------------------")
