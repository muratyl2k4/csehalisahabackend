from rest_framework import serializers
from .models import Match, PlayerMatchStats
from teams.serializers import TeamListSerializer


class PlayerMatchStatsSerializer(serializers.ModelSerializer):
    """Player's performance statistics in a match serializer"""
    player_name = serializers.CharField(source='player.name', read_only=True)
    player_photo = serializers.ImageField(source='player.photo', read_only=True)
    player_id = serializers.IntegerField(source='player.id', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = PlayerMatchStats
        fields = ['id', 'player_id', 'player_name', 'player_photo', 'team_name', 'goals', 'assists', 'played']


class MatchListSerializer(serializers.ModelSerializer):
    """Match list serializer"""
    team1_name = serializers.CharField(source='team1.name', read_only=True)
    team2_name = serializers.CharField(source='team2.name', read_only=True)
    team1_short_name = serializers.CharField(source='team1.short_name', read_only=True)
    team2_short_name = serializers.CharField(source='team2.short_name', read_only=True)
    team1_logo = serializers.ImageField(source='team1.logo', read_only=True)
    team2_logo = serializers.ImageField(source='team2.logo', read_only=True)
    winner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'date', 
            'team1', 'team1_name', 'team1_short_name', 'team1_logo', 'team1_score',
            'team2', 'team2_name', 'team2_short_name', 'team2_logo', 'team2_score',
            'is_finished', 'winner_name'
        ]
    
    def get_winner_name(self, obj):
        winner = obj.winner
        return winner.name if winner else 'Beraberlik' if obj.is_finished else 'Devam Ediyor'


class MatchDetailSerializer(serializers.ModelSerializer):
    """Match detail serializer - with player statistics"""
    team1_info = TeamListSerializer(source='team1', read_only=True)
    team2_info = TeamListSerializer(source='team2', read_only=True)
    team1_players = serializers.SerializerMethodField()
    team2_players = serializers.SerializerMethodField()
    winner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'date',
            'team1_info', 'team1_score', 'team1_players',
            'team2_info', 'team2_score', 'team2_players',
            'is_finished', 'winner_name', 'created_at'
        ]
    
    def get_team1_players(self, obj):
        """Get team 1 players statistics"""
        stats = PlayerMatchStats.objects.filter(
            match=obj,
            team=obj.team1
        ).select_related('player')
        return PlayerMatchStatsSerializer(stats, many=True, context=self.context).data
    
    def get_team2_players(self, obj):
        """Get team 2 players statistics"""
        stats = PlayerMatchStats.objects.filter(
            match=obj,
            team=obj.team2
        ).select_related('player')
        return PlayerMatchStatsSerializer(stats, many=True, context=self.context).data
    
    def get_winner_name(self, obj):
        winner = obj.winner
        return winner.name if winner else 'Beraberlik' if obj.is_finished else 'Devam Ediyor'


class PlayerMatchHistorySerializer(serializers.ModelSerializer):
    """Player match history serializer"""
    match_date = serializers.DateTimeField(source='match.date', read_only=True)
    match_id = serializers.IntegerField(source='match.id', read_only=True)
    team1_name = serializers.CharField(source='match.team1.name', read_only=True)
    team2_name = serializers.CharField(source='match.team2.name', read_only=True)
    team1_short_name = serializers.CharField(source='match.team1.short_name', read_only=True)
    team2_short_name = serializers.CharField(source='match.team2.short_name', read_only=True)
    team1_score = serializers.IntegerField(source='match.team1_score', read_only=True)
    team2_score = serializers.IntegerField(source='match.team2_score', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = PlayerMatchStats
        fields = [
            'match_id', 'match_date',
            'team_name', 'team1_name', 'team2_name',
            'team1_short_name', 'team2_short_name',
            'team1_score', 'team2_score',
            'goals', 'assists', 'played'
        ]
