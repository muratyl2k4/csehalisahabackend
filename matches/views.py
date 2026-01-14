from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Match, PlayerMatchStats
from .serializers import MatchListSerializer, MatchDetailSerializer


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    MatchViewSet
    
    list: List all matches (sorted by latest first)
    retrieve: Get match details (with player statistics)
    """
    queryset = Match.objects.all().select_related('team1', 'team2')
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchListSerializer
    
    def get_queryset(self):
        """En son oynanandan başlayarak sırala ve takım filtresi uygula"""
        queryset = Match.objects.all().select_related('team1', 'team2').order_by('-date')
        
        team_id = self.request.query_params.get('team', None)
        player_id = self.request.query_params.get('player', None)
        
        #?team=id
        if team_id is not None:
            queryset = queryset.filter(Q(team1_id=team_id) | Q(team2_id=team_id))

        #?player=id
        elif player_id is not None:
            queryset = queryset.filter(Q(team1_playermatchstats__player_id=player_id) | Q(team2_playermatchstats__player_id=player_id))

        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def recent_matches(request):
    """Get last 3 matches (home screen endpoint)"""
    matches = Match.objects.all().select_related('team1', 'team2').order_by('-date')[:3]
    serializer = MatchListSerializer(matches, many=True, context={'request': request})
    return Response(serializer.data)
