from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum, Count
from .models import Player
from .serializers import (
    PlayerListSerializer,
    PlayerDetailSerializer,
    LeaderboardSerializer,
    LeaderboardSerializer,
    PlayerRegisterSerializer,
    EmailTokenObtainPairSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = Player.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = PlayerRegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    Oyuncular için ViewSet
    
    list: Tüm oyuncuları listele
    retrieve: Tek bir oyuncunun detaylarını getir
    """
    # queryset = Player.objects.all().select_related('current_team') # Moved to get_queryset
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Listelemede sadece takımı olanları göster ve overall'a göre sırala.
        Detayda herkesi göster.
        """
        qs = Player.objects.select_related('current_team').order_by('-overall')
        
        # if self.action == 'list':
        #     qs = qs.filter(current_team__isnull=False)
            
        return qs
    
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
