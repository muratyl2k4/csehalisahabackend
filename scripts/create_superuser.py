import os
import sys
import django

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from players.models import Player

username = 'admin'
email = 'admin@example.com'
password = 'admin'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created.")
    
    # Create Player Profile for Admin
    if not hasattr(user, 'player_profile'):
        print("Creating Player profile for admin...")
        Player.objects.create(
            user=user,
            name='Admin User',
            position='MO',
            age=25,
            overall=99 # Admin power!
        )
        print("Player profile created.")
else:
    print("Superuser already exists.")
