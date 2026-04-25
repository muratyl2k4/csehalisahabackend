from rest_framework import serializers
from .models import League, Week, Standing, Tournament, TournamentMatch
from teams.serializers import TeamListSerializer
from matches.serializers import MatchListSerializer

class TournamentMatchSerializer(serializers.ModelSerializer):
    """Tournament Match Serializer - Directly includes Match fields"""
    team1_name = serializers.ReadOnlyField(source='team1.name')
    team1_logo = serializers.ImageField(source='team1.logo', read_only=True)
    team2_name = serializers.ReadOnlyField(source='team2.name')
    team2_logo = serializers.ImageField(source='team2.logo', read_only=True)
    
    class Meta:
        model = TournamentMatch
        fields = [
            'id', 'round_name', 'round_index', 'position',
            'team1', 'team1_name', 'team1_logo',
            'team2', 'team2_name', 'team2_logo',
            'next_match', 'date', 'team1_score', 'team2_score', 'is_finished', 'is_live'
        ]

class TournamentSerializer(serializers.ModelSerializer):
    """Tournament Serializer including Matches"""
    matches = TournamentMatchSerializer(source='tournament_matches', many=True, read_only=True)
    
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'matches']

class LeagueSerializer(serializers.ModelSerializer):
    """League Serializer"""
    class Meta:
        model = League
        fields = ['id', 'name', 'season', 'is_active', 'created_at']

class LeagueDetailSerializer(serializers.ModelSerializer):
    """Detailed League Serializer including Tournament"""
    tournament = TournamentSerializer(read_only=True)
    
    class Meta:
        model = League
        fields = ['id', 'name', 'season', 'is_active', 'created_at', 'tournament']

class WeekSerializer(serializers.ModelSerializer):
# ... rest of file ...
    """Week Serializer with Matches"""
    class Meta:
        model = Week
        fields = ['id', 'league', 'name', 'start_date', 'end_date', 'is_played']


class StandingSerializer(serializers.ModelSerializer):
    """Standing Serializer including Team Info"""
    team_name = serializers.ReadOnlyField(source='team.name')
    team_logo = serializers.ImageField(source='team.logo', read_only=True)
    league_name = serializers.ReadOnlyField(source='league.name')
    goal_difference = serializers.ReadOnlyField()
    
    class Meta:
        model = Standing
        fields = ['id', 'league', 'league_name', 'team', 'team_name', 'team_logo', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_difference', 'points']
