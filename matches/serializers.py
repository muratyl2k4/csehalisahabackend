from rest_framework import serializers
from .models import Match, PlayerMatchStats, PlayerMatchRating
from teams.serializers import TeamListSerializer


class PlayerMatchStatsSerializer(serializers.ModelSerializer):
    """Player's performance statistics in a match serializer"""
    player_name = serializers.CharField(source='player.name', read_only=True)
    player_photo = serializers.ImageField(source='player.photo', read_only=True)
    player_id = serializers.IntegerField(source='player.id', read_only=True)
    player_user_id = serializers.IntegerField(source='player.user.id', read_only=True)
    jersey_number = serializers.IntegerField(source='player.jersey_number', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = PlayerMatchStats
        fields = ['id', 'player_id', 'player_user_id', 'player_name', 'player_photo', 'jersey_number', 'team_name', 'goals', 'assists', 'yellow_cards', 'red_cards', 'played']


class MatchListSerializer(serializers.ModelSerializer):
    """Match list serializer"""
    team1_name = serializers.CharField(source='team1.name', read_only=True)
    team2_name = serializers.CharField(source='team2.name', read_only=True)
    team1_short_name = serializers.CharField(source='team1.short_name', read_only=True)
    team2_short_name = serializers.CharField(source='team2.short_name', read_only=True)
    team1_logo = serializers.ImageField(source='team1.logo', read_only=True)
    team2_logo = serializers.ImageField(source='team2.logo', read_only=True)
    winner_name = serializers.SerializerMethodField()
    voting_open = serializers.SerializerMethodField()
    
    # New Architecture Fields
    week_name = serializers.CharField(source='week.name', read_only=True, default="Belirsiz")
    league_id = serializers.IntegerField(source='week.league.id', read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'date', 'match_type', 'week', 'week_name', 'league_id',
            'team1', 'team1_name', 'team1_short_name', 'team1_logo', 'team1_score', 'team1_penalties',
            'team2', 'team2_name', 'team2_short_name', 'team2_logo', 'team2_score', 'team2_penalties',
            'is_finished', 'finished_at', 'voting_open', 'is_live', 'winner_name', 'is_score_editable'
        ]
    
    def get_winner_name(self, obj):
        winner = obj.winner
        return winner.name if winner else 'Beraberlik' if obj.is_finished else 'Devam Ediyor'
    
    def get_voting_open(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        if not obj.is_finished or not obj.finished_at:
            return False
        return timezone.now() < obj.finished_at + timedelta(hours=3)


class MatchDetailSerializer(serializers.ModelSerializer):
    """Match detail serializer - with player statistics"""
    team1_info = TeamListSerializer(source='team1', read_only=True)
    team2_info = TeamListSerializer(source='team2', read_only=True)
    team1_players = serializers.SerializerMethodField()
    team2_players = serializers.SerializerMethodField()
    winner_name = serializers.SerializerMethodField()
    
    week_name = serializers.CharField(source='week.name', read_only=True)
    league_id = serializers.IntegerField(source='week.league.id', read_only=True)
    
    voting_open = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'date', 'match_type', 'week', 'week_name', 'league_id',
            'team1_info', 'team1_score', 'team1_penalties', 'team1_players',
            'team2_info', 'team2_score', 'team2_penalties', 'team2_players',
            'is_finished', 'finished_at', 'voting_open', 'is_live', 'winner_name', 'created_at',
            'referee', 'is_score_editable'
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
    
    def get_voting_open(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        if not obj.is_finished or not obj.finished_at:
            return False
        return timezone.now() < obj.finished_at + timedelta(hours=3)


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
        fields = [
            'id', 'match_date', 'match_id', 'team1_name', 'team2_name',
            'team1_short_name', 'team2_short_name', 'team1_score', 'team2_score',
            'team_name'
        ]
        model = PlayerMatchStats

class PlayerMatchRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for submitting player ratings.
    """
    rater_name = serializers.CharField(source='rater.name', read_only=True)
    rated_player_name = serializers.CharField(source='rated_player.name', read_only=True)
    
    class Meta:
        model = PlayerMatchRating
        fields = [
            'id', 'match', 'rater', 'rater_name', 'rated_player', 'rated_player_name',
            'rating_pace', 'rating_shooting', 'rating_passing', 
            'rating_dribbling', 'rating_defense', 'rating_physical',
            'comment', 'average_score_10', 'normalized_score', 'created_at'
        ]
        read_only_fields = ['rater', 'match', 'average_score_10', 'normalized_score', 'created_at']

