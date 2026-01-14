from rest_framework import serializers
from .models import Team, TransferRequest


class TransferRequestSerializer(serializers.ModelSerializer):
    """Transfer request serializer"""
    player_name = serializers.CharField(source='player.name', read_only=True)
    player_photo = serializers.ImageField(source='player.photo', read_only=True)
    player_position = serializers.CharField(source='player.position', read_only=True)
    player_overall = serializers.IntegerField(source='player.overall', read_only=True)
    
    class Meta:
        model = TransferRequest
        fields = ['id', 'player', 'player_name', 'player_photo', 'player_position', 'player_overall', 'team', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']


class TeamListSerializer(serializers.ModelSerializer):
    """Team list serializer"""
    total_matches = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    draws = serializers.ReadOnlyField()
    
    goal_difference = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'short_name', 'logo', 'wins', 'losses', 'draws', 'goals_scored', 'goals_conceded', 'goal_difference', 'points', 'total_matches', 'win_rate', 'created_at']
        read_only_fields = ['wins', 'losses', 'draws', 'goals_scored', 'goals_conceded', 'points', 'created_at']


class TeamCreateSerializer(serializers.ModelSerializer):
    """Team create serializer"""
    class Meta:
        model = Team
        fields = ['name', 'short_name', 'logo']


class TeamUpdateSerializer(serializers.ModelSerializer):
    """Team update serializer (Only allowed fields)"""
    class Meta:
        model = Team
        fields = ['name', 'short_name', 'logo']


class TeamDetailSerializer(serializers.ModelSerializer):
    """Team detail serializer"""
    total_matches = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    draws = serializers.ReadOnlyField()
    goal_difference = serializers.ReadOnlyField()
    players = serializers.SerializerMethodField()
    recent_matches = serializers.SerializerMethodField()
    captain_id = serializers.ReadOnlyField(source='captain.id')
    captain_name = serializers.ReadOnlyField(source='captain.name')
    pending_requests = serializers.SerializerMethodField()
    user_request_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'short_name', 'logo', 'wins', 'losses', 'draws', 'goals_scored', 'goals_conceded', 'goal_difference', 'points', 'total_matches', 'win_rate', 'captain_id', 'captain_name', 'players', 'recent_matches', 'pending_requests', 'user_request_status', 'created_at']
        read_only_fields = ['wins', 'losses', 'draws', 'goals_scored', 'goals_conceded', 'points', 'created_at']
    
    def get_players(self, obj):
        """Get team players"""
        from players.serializers import PlayerListSerializer
        # Optimize: Prefetch user to avoid N+1 when serializing 'username'
        players = obj.players.all().select_related('user')
        return PlayerListSerializer(players, many=True, context=self.context).data

    def get_recent_matches(self, obj):
        """Get team's last 5 matches"""
        from matches.models import Match
        from matches.serializers import MatchListSerializer
        from django.db.models import Q
        
        matches = Match.objects.filter(
            Q(team1=obj) | Q(team2=obj)
        ).order_by('-date')[:5]
        
        return MatchListSerializer(matches, many=True, context=self.context).data

    def get_pending_requests(self, obj):
        """Show pending requests only for captains"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if user is the captain of THIS team
            # Note: request.user.player_profile might not exist if user is superuser without profile, handle potential error
            try:
                if hasattr(request.user, 'player_profile') and obj.captain == request.user.player_profile:
                    requests = TransferRequest.objects.filter(team=obj, status='PENDING')
                    return TransferRequestSerializer(requests, many=True, context=self.context).data
            except Exception as e:
                pass
        return []

    def get_user_request_status(self, obj):
        """Check if the logged in user has a pending request for this team"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
             try:
                if hasattr(request.user, 'player_profile'):
                    req = TransferRequest.objects.filter(
                        team=obj, 
                        player=request.user.player_profile,
                        status='PENDING'
                    ).first()
                    if req:
                        return 'PENDING'
             except:
                 pass
        return None
