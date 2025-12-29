from rest_framework import serializers
from .models import Player
from teams.models import Team


class PlayerListSerializer(serializers.ModelSerializer):
    """Oyuncu listesi için serializer"""
    total_goals = serializers.ReadOnlyField()
    total_assists = serializers.ReadOnlyField()
    matches_played = serializers.ReadOnlyField()
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    current_team_logo = serializers.ImageField(source='current_team.logo', read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'name', 'age', 'photo', 'position',
            'current_team', 'current_team_name', 'current_team_logo',
            'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
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
    match_history = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'name', 'age', 'photo', 'position',
            'current_team', 'current_team_name', 'current_team_logo',
            'overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
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
