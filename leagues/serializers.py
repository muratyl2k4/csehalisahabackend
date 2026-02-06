from rest_framework import serializers
from .models import League, Week, Standing
from teams.serializers import TeamListSerializer
from matches.serializers import MatchListSerializer

class LeagueSerializer(serializers.ModelSerializer):
    """League Serializer"""
    class Meta:
        model = League
        fields = ['id', 'name', 'season', 'is_active', 'created_at']


class WeekSerializer(serializers.ModelSerializer):
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
