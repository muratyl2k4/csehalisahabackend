from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum, Count
from .models import Player
from .serializers import PlayerListSerializer, PlayerDetailSerializer, LeaderboardSerializer


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Oyuncular için ViewSet
    
    list: Tüm oyuncuları listele
    retrieve: Tek bir oyuncunun detaylarını getir
    """
    queryset = Player.objects.all().select_related('current_team')
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlayerDetailSerializer
        return PlayerListSerializer
    
    @action(detail=False, methods=['get'], url_path='leaderboard/goals')
    def goal_leaderboard(self, request):
        """
        Gol krallığı tablosu
        GET /api/players/leaderboard/goals/
        """
        from matches.models import PlayerMatchStats
        
        # Oyuncuları gol sayısına göre sırala
        player_goals = PlayerMatchStats.objects.values('player').annotate(
            total_goals=Sum('goals')
        ).filter(total_goals__gt=0).order_by('-total_goals')
        
        # Player ID'lerini al
        player_ids = [pg['player'] for pg in player_goals]
        
        # Oyuncuları getir ve sırala
        players = Player.objects.filter(id__in=player_ids)
        
        # Manuel olarak sırala (toplam gol sayısına göre)
        players_list = list(players)
        players_list.sort(key=lambda p: p.total_goals, reverse=True)
        
        serializer = LeaderboardSerializer(players_list, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='leaderboard/assists')
    def assist_leaderboard(self, request):
        """
        Asist krallığı tablosu
        GET /api/players/leaderboard/assists/
        """
        from matches.models import PlayerMatchStats
        
        # Oyuncuları asist sayısına göre sırala
        player_assists = PlayerMatchStats.objects.values('player').annotate(
            total_assists=Sum('assists')
        ).filter(total_assists__gt=0).order_by('-total_assists')
        
        # Player ID'lerini al
        player_ids = [pa['player'] for pa in player_assists]
        
        # Oyuncuları getir ve sırala
        players = Player.objects.filter(id__in=player_ids)
        
        # Manuel olarak sırala (toplam asist sayısına göre)
        players_list = list(players)
        players_list.sort(key=lambda p: p.total_assists, reverse=True)
        
        serializer = LeaderboardSerializer(players_list, many=True, context={'request': request})
        return Response(serializer.data)
