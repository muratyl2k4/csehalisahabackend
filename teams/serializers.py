from rest_framework import serializers
from .models import Team


class TeamListSerializer(serializers.ModelSerializer):
    """Takım listesi için serializer"""
    total_matches = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    draws = serializers.ReadOnlyField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'short_name', 'logo', 'wins', 'losses', 'draws', 'total_matches', 'win_rate', 'created_at']


class TeamDetailSerializer(serializers.ModelSerializer):
    """Takım detay için serializer"""
    total_matches = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    draws = serializers.ReadOnlyField()
    players = serializers.SerializerMethodField()
    recent_matches = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'logo', 'wins', 'losses', 'draws', 'total_matches', 'win_rate', 'players', 'recent_matches', 'created_at']
    
    def get_players(self, obj):
        """Takımın oyuncularını getir"""
        from players.serializers import PlayerListSerializer
        players = obj.players.all()
        return PlayerListSerializer(players, many=True, context=self.context).data

    def get_recent_matches(self, obj):
        """Takımın son 5 maçını getir"""
        from matches.models import Match
        from matches.serializers import MatchListSerializer
        from django.db.models import Q
        
        matches = Match.objects.filter(
            Q(team1=obj) | Q(team2=obj)
        ).order_by('-date')[:5]
        
        return MatchListSerializer(matches, many=True, context=self.context).data
