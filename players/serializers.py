from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Player
from teams.models import Team

from django.utils import timezone
from django.utils.text import slugify
import uuid
import random
from utils.email_service import EmailService

class PlayerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=True)
    
    
    # Player profile fields
    name = serializers.CharField(required=True, max_length=30)
    position = serializers.ChoiceField(choices=Player.POSITION_CHOICES, required=True)

    def validate_name(self, value):
        import re
        # Regex: only letters (include turkish letters) and spaces. No numbers or symbols.
        if not re.match(r'^[a-zA-ZçÇğĞıİöÖşŞüÜ\s]+$', value):
            raise serializers.ValidationError("İsim sadece harflerden oluşmalıdır. Özel karakter veya sayı kullanılamaz.")
        if len(value) < 3:
             raise serializers.ValidationError("İsim en az 3 karakter olmalıdır.")
        return value
    
    class Meta:
        model = Player
        fields = ('password', 'email', 'name', 'position', 'age', 'overall', 'photo', 'jersey_number', 'preferred_foot')
        read_only_fields = ('overall',)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu E-posta adresi zaten kullanımda.")
        return value

    def create(self, validated_data):
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # 1. Generate unique username
                base_username = slugify(validated_data['name']).replace('-', '') or 'user'
                unique_suffix = uuid.uuid4().hex[:6]
                generated_username = f"{base_username}_{unique_suffix}"
    
                # CREATE USER
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
                
                # CREATE PLAYER PROFILE
                verification_code = str(random.randint(100000, 999999))
                player = Player.objects.create(
                    user=user, 
                    verification_code=verification_code,
                    verification_code_created_at=timezone.now(),
                    **validated_data
                )
                
                # VERIFICATION EMAIL
                EmailService.send_html(
                    'Akdeniz CSE Halısaha - E-posta Doğrulama',
                    'emails/verification.html',
                    {'name': first_name, 'code': verification_code},
                    [user.email]
                )
                
                
                player.save() 

                # Welcome Notification
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=user,
                    message="Hoş geldiniz! Hesabınız başarıyla oluşturuldu. Keyifli vakitler dileriz.",
                    notification_type='SYSTEM'
                )

                return player
        except Exception as e:
            # SEND ERROR TO CLIENT
            raise e

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # FRONTEND USERNAME -> EMAIL
        email = attrs.get('username') 
        password = attrs.get('password')

        if email and password:
            try:
                
                user_obj = User.objects.get(email=email)
                username = user_obj.username
                
                
                user = authenticate(username=username, password=password)
                
                if user:
                     
                    data = super().validate({'username': username, 'password': password})
                    
                  
                    data['username'] = user.username
                    data['email'] = user.email
                    if hasattr(user, 'player_profile'):
                        data['name'] = user.player_profile.name
                        data['id'] = user.player_profile.id
                        data['photo'] = user.player_profile.photo.url if user.player_profile.photo else None
                        data['id'] = user.player_profile.id
                        data['photo'] = user.player_profile.photo.url if user.player_profile.photo else None
                        data['current_team'] = user.player_profile.current_team.id if user.player_profile.current_team else None
                        data['current_team'] = user.player_profile.current_team.id if user.player_profile.current_team else None
                        data['current_team'] = user.player_profile.current_team.id if user.player_profile.current_team else None
                        data['is_email_verified'] = user.player_profile.is_email_verified
                        data['jersey_number'] = user.player_profile.jersey_number
                        data['preferred_foot'] = user.player_profile.preferred_foot
                    
                    data['is_staff'] = user.is_staff 
                    
                    return data
            except User.DoesNotExist:
                pass
        
        # IF FAILS
        raise serializers.ValidationError('No active account found with the given credentials')

class PlayerListSerializer(serializers.ModelSerializer):
    """Player list serializer"""
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
            'created_at', 'jersey_number', 'preferred_foot'
        ]
        read_only_fields = [
            'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
            'diving', 'handling', 'kicking', 'reflexes', 'speed', 'positioning',
            'total_goals', 'total_assists', 'matches_played', 'username', 'created_at'
        ]

class PlayerDetailSerializer(serializers.ModelSerializer):
    """Player detail serializer"""
    total_goals = serializers.ReadOnlyField()
    total_assists = serializers.ReadOnlyField()
    matches_played = serializers.ReadOnlyField()
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    current_team_logo = serializers.ImageField(source='current_team.logo', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    match_history = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'username', 'email', 'name', 'age', 'photo', 'position',
            'current_team', 'current_team_name', 'current_team_logo',
            'jersey_number', 'preferred_foot',
            'overall', 
            # Outfield Stats
            'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
            # GK Stats
            'diving', 'handling', 'kicking', 'reflexes', 'speed', 'positioning',
            'total_goals', 'total_assists', 'matches_played',
            'match_history',
            'created_at', 'updated_at', 'is_email_verified'
        ]
        read_only_fields = [
            'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
            'diving', 'handling', 'kicking', 'reflexes', 'speed', 'positioning',
            'total_goals', 'total_assists', 'matches_played', 
            'current_team', 'username', 'email'
        ]
    
    def get_match_history(self, obj):
        """Get player match history"""
        from matches.models import PlayerMatchStats
        from matches.serializers import PlayerMatchHistorySerializer
        
        stats = PlayerMatchStats.objects.filter(
            player=obj,
            played=True
        ).select_related('match', 'team').order_by('-match__date')
        
        return PlayerMatchHistorySerializer(stats, many=True).data

class LeaderboardSerializer(serializers.ModelSerializer):
    """Leaderboard serializer"""
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

class PlayerUpdateSerializer(serializers.ModelSerializer):
    """Self Update Serializer for users"""
    name = serializers.CharField(required=False, max_length=30)
    position = serializers.ChoiceField(choices=Player.POSITION_CHOICES, required=False)
    photo = serializers.ImageField(required=False, allow_null=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = Player
    preferred_foot = serializers.ChoiceField(choices=Player.FOOT_CHOICES, required=False)
    jersey_number = serializers.IntegerField(required=False, min_value=1, max_value=99)

    class Meta:
        model = Player
        fields = ['name', 'position', 'photo', 'email', 'jersey_number', 'preferred_foot']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Bu E-posta adresi zaten kullanımda.")
        return value

    def validate_name(self, value):
        import re
        if not re.match(r'^[a-zA-ZçÇğĞıİöÖşŞüÜ\s]+$', value):
            raise serializers.ValidationError("İsim sadece harflerden oluşmalıdır.")
        if len(value) < 3:
             raise serializers.ValidationError("İsim en az 3 karakter olmalıdır.")
        return value

    def update(self, instance, validated_data):
        # Update Player fields
        for attr, value in validated_data.items():
            if attr != 'email': # Handle email separately
                setattr(instance, attr, value)
        
        # Sync Name to User model if changed
        user = instance.user
        if 'name' in validated_data:
            name_parts = validated_data['name'].strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            user.first_name = first_name
            user.last_name = last_name
        
        # Handle Email Change
        if 'email' in validated_data and validated_data['email'] != user.email:
            new_email = validated_data['email']
            user.email = new_email
            
            # Generate new code
            import random
            verification_code = str(random.randint(100000, 999999))
            
            instance.is_email_verified = False # Reset verification
            instance.verification_code = verification_code
            instance.verification_code_created_at = timezone.now()
            
            # Send Verification Email
            EmailService.send_html(
                'Akdeniz CSE Halısaha - E-posta Değişikliği Doğrulama',
                'emails/verification.html',
                {'name': instance.name, 'code': verification_code},
                [new_email]
            )
        
        user.save()

        # Save Player (triggers overall recalculation and photo processing in model.save())
        ##TODO make this trigger with signals.
        instance.save()
        return instance
