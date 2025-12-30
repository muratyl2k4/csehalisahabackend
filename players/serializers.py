from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Player
from teams.models import Team

from django.utils.text import slugify
import uuid

class PlayerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    
    # Player profile fields
    name = serializers.CharField(required=True)
    position = serializers.ChoiceField(choices=Player.POSITION_CHOICES, required=True)
    
    class Meta:
        model = Player
        fields = ('password', 'email', 'name', 'position', 'age', 'overall', 'photo')
        read_only_fields = ('overall',)

    def create(self, validated_data):
        # 1. Generate unique username
        base_username = slugify(validated_data['name']).replace('-', '') or 'user'
        unique_suffix = uuid.uuid4().hex[:6]
        generated_username = f"{base_username}_{unique_suffix}"

        # 2. Create User
        name_parts = validated_data['name'].strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user_data = {
            'username': generated_username,
            'password': validated_data.pop('password'),
            'email': validated_data.get('email', ''),
            'first_name': first_name,
            'last_name': last_name
        }
        if 'email' in validated_data: validated_data.pop('email')
        
        user = User.objects.create_user(**user_data)
        
        # 3. Create Player Profile
        player = Player.objects.create(user=user, **validated_data)
        
        # Calculate overall on creation
        player.save() 
        return player

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Username field sent from frontend -> treated as email
        email = attrs.get('username') 
        password = attrs.get('password')

        if email and password:
            try:
                # Find user by email
                user_obj = User.objects.get(email=email)
                username = user_obj.username
                
                # Authenticate with found username
                user = authenticate(username=username, password=password)
                
                if user:
                     # Add token logic from parent
                    data = super().validate({'username': username, 'password': password})
                    
                    # Custom Data in Response
                    data['username'] = user.username
                    data['email'] = user.email
                    if hasattr(user, 'player_profile'):
                        data['name'] = user.player_profile.name
                        data['id'] = user.player_profile.id
                        data['photo'] = user.player_profile.photo.url if user.player_profile.photo else None
                        data['current_team'] = user.player_profile.current_team.id if user.player_profile.current_team else None
                    
                    return data
            except User.DoesNotExist:
                pass
        
        # If fetch fails or auth fails
        raise serializers.ValidationError('No active account found with the given credentials')

class PlayerListSerializer(serializers.ModelSerializer):
    """Oyuncu listesi için serializer"""
    total_goals = serializers.ReadOnlyField()
    total_assists = serializers.ReadOnlyField()
    matches_played = serializers.ReadOnlyField()
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    current_team_logo = serializers.ImageField(source='current_team.logo', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'username', 'name', 'age', 'photo', 'position',
            'current_team', 'current_team_name', 'current_team_logo',
            'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
            'diving', 'handling', 'kicking', 'reflexes', 'speed', 'positioning',
            'total_goals', 'total_assists', 'matches_played',
            'created_at'
        ]

class PlayerDetailSerializer(serializers.ModelSerializer):
    """Oyuncu detay için serializer"""
    total_goals = serializers.ReadOnlyField()
    total_assists = serializers.ReadOnlyField()
    matches_played = serializers.ReadOnlyField()
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    current_team_logo = serializers.ImageField(source='current_team.logo', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    match_history = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'username', 'name', 'age', 'photo', 'position',
            'current_team', 'current_team_name', 'current_team_logo',
            'overall', 
            # Outfield Stats
            'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
            # GK Stats
            'diving', 'handling', 'kicking', 'reflexes', 'speed', 'positioning',
            'total_goals', 'total_assists', 'matches_played',
            'match_history',
            'created_at', 'updated_at'
        ]
    
    def get_match_history(self, obj):
        """Oyuncunun maç geçmişini getir"""
        from matches.models import PlayerMatchStats
        from matches.serializers import PlayerMatchHistorySerializer
        
        stats = PlayerMatchStats.objects.filter(
            player=obj,
            played=True
        ).select_related('match', 'team').order_by('-match__date')
        
        return PlayerMatchHistorySerializer(stats, many=True).data

class LeaderboardSerializer(serializers.ModelSerializer):
    """Liderlik tablosu için serializer"""
    total_goals = serializers.ReadOnlyField()
    total_assists = serializers.ReadOnlyField()
    matches_played = serializers.ReadOnlyField()
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    current_team_logo = serializers.ImageField(source='current_team.logo', read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'name', 'photo', 'position',
            'current_team_name', 'current_team_logo',
            'total_goals', 'total_assists', 'matches_played'
        ]
