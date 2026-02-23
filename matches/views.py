from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend # Added import
from .models import Match, PlayerMatchStats
from .serializers import MatchListSerializer, MatchDetailSerializer
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

# ... existing code ...

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    MatchViewSet
    
    list: List all matches
    retrieve: Get match details
    filterset_fields: is_finished, week, week__league
    ordering_fields: date
    """
    queryset = Match.objects.all().select_related('team1', 'team2')
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['date']
    filterset_fields = ['is_finished', 'week', 'week__league']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchListSerializer
    
    def get_queryset(self):
        # ... same as before ...
        queryset = Match.objects.all().select_related('team1', 'team2').order_by('-date')
        
        team_id = self.request.query_params.get('team', None)
        player_id = self.request.query_params.get('player', None)
        
        if team_id is not None:
            queryset = queryset.filter(Q(team1_id=team_id) | Q(team2_id=team_id))

        if player_id is not None:
             queryset = queryset.filter(player_stats__player_id=player_id).distinct()
        
        return queryset

    # ... existing rate_player ...
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate_player(self, request, pk=None):
        match = self.get_object()
        user = request.user
        
        try:
            rater = user.player_profile
        except:
            return Response({"detail": "Oyuncu profiliniz bulunamadı."}, status=status.HTTP_400_BAD_REQUEST)

        rated_player_id = request.data.get('rated_player_id')
        ratings_data = request.data.get('ratings', {})
        comment = request.data.get('comment', '')

        if not rated_player_id:
            return Response({"detail": "Oylanacak oyuncu seçilmedi."}, status=status.HTTP_400_BAD_REQUEST)

        # Allow rating only if match is finished
        if not match.is_finished:
            return Response({"detail": "Maç henüz bitmediği için oylama yapılamaz."}, status=status.HTTP_400_BAD_REQUEST)

        # 3 hour voting window
        if match.finished_at:
            voting_deadline = match.finished_at + timedelta(hours=3)
            if timezone.now() > voting_deadline:
                return Response({"detail": "Oylama süresi doldu. Maç bittikten sonra 3 saat içinde oy kullanabilirsiniz."}, status=status.HTTP_400_BAD_REQUEST)

        if rater.id == int(rated_player_id):
            return Response({"detail": "Kendinize oy veremezsiniz."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already rated
        from .models import PlayerMatchRating
        if PlayerMatchRating.objects.filter(match=match, rater=rater, rated_player_id=rated_player_id).exists():
             return Response({"detail": "Bu oyuncuyu bu maç için zaten oyladınız."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = PlayerMatchRating.objects.create(
                match=match,
                rater=rater,
                rated_player_id=rated_player_id,
                rating_pace=ratings_data.get('pace', 5),
                rating_shooting=ratings_data.get('shooting', 5),
                rating_passing=ratings_data.get('passing', 5),
                rating_dribbling=ratings_data.get('dribbling', 5),
                rating_defense=ratings_data.get('defense', 5),
                rating_physical=ratings_data.get('physical', 5),
                # GK
                rating_diving=ratings_data.get('diving', 5),
                rating_handling=ratings_data.get('handling', 5),
                rating_kicking=ratings_data.get('kicking', 5),
                rating_reflexes=ratings_data.get('reflexes', 5),
                rating_speed=ratings_data.get('speed', 5),
                rating_positioning=ratings_data.get('positioning', 5),
                comment=comment
            )
            
            # RatingService is now triggered by signals (post_save on PlayerMatchRating)
            # from .services import RatingService
            # RatingService.update_player_overall(rated_player_id, new_rating=rating)

            return Response({"detail": "Oylama başarıyla kaydedildi."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def record_goal(self, request, pk=None):
        """
        Record a goal for a specific team.
        Can be an Own Goal (direct score update) or a Player Goal (updates stats + signal updates score).
        Body: { "team_id": 1, "player_id": 2, "assist_player_id": 3, "own_goal": false }
        """
        match = self.get_object()
        user = request.user
        
        # Permission Check
        is_referee = match.referee == user
        is_admin = user.is_staff
        
        if not (is_referee or is_admin):
            return Response({"detail": "Bu işlem için yetkiniz yok."}, status=status.HTTP_403_FORBIDDEN)
            
        if not match.is_score_editable and not is_admin:
             return Response({"detail": "Maç skoru şu an düzenlenemez."}, status=status.HTTP_400_BAD_REQUEST)

        team_id = request.data.get('team_id')
        player_id = request.data.get('player_id')
        assist_player_id = request.data.get('assist_player_id')
        own_goal = request.data.get('own_goal', False)

        if not team_id:
             return Response({"detail": "Takım seçilmedi."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if own_goal:
                # Direct score update for the selected team
                if int(team_id) == match.team1.id:
                    match.team1_score += 1
                elif int(team_id) == match.team2.id:
                    match.team2_score += 1
                match.save()
                return Response({"detail": "Kendi kalesine (veya rakip hediye) gol kaydedildi. Skor güncellendi."})
            
            # Player Goal
            if not player_id:
                 return Response({"detail": "Golü atan oyuncu seçilmedi."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Check Scorer (Before saving)
                scorer_stats = PlayerMatchStats.objects.select_for_update().get(match=match, player_id=player_id)
                
                # Check Assist (Before saving scorer)
                if assist_player_id:
                     assist_stats = PlayerMatchStats.objects.select_for_update().get(match=match, player_id=assist_player_id)
                
                
                scorer_stats.goals += 1
                scorer_stats.save()

                if assist_player_id:
                    assist_stats.assists += 1
                    assist_stats.save()
                    
                return Response({"detail": f"Gol kaydedildi: {scorer_stats.player.name}"})
            
            except PlayerMatchStats.DoesNotExist:
                 return Response({"detail": "Oyuncu bu maçta bulunamadı."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def record_card(self, request, pk=None):
        """
        Record a card for a player.
        Body: { "player_id": 1, "card_type": "yellow" | "red" }
        """
        match = self.get_object()
        user = request.user
        
        # Permission Check (Same as above)
        is_referee = match.referee == user
        is_admin = user.is_staff
        
        if not (is_referee or is_admin):
            return Response({"detail": "Bu işlem için yetkiniz yok."}, status=status.HTTP_403_FORBIDDEN)
            
        if not match.is_score_editable and not is_admin:
             return Response({"detail": "Maç skoru şu an düzenlenemez."}, status=status.HTTP_400_BAD_REQUEST)

        player_id = request.data.get('player_id')
        card_type = request.data.get('card_type')
        
        if not player_id or not card_type:
             return Response({"detail": "Eksik bilgi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stats = PlayerMatchStats.objects.get(match=match, player_id=player_id)
            
            if card_type == 'yellow':
                stats.yellow_cards += 1
            elif card_type == 'red':
                stats.red_cards += 1
                
            stats.save()
            return Response({"detail": f"{card_type == 'yellow' and 'Sarı' or 'Kırmızı'} kart kaydedildi: {stats.player.name}"})

        except PlayerMatchStats.DoesNotExist:
             return Response({"detail": "Oyuncu bu maçta bulunamadı."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_match(self, request, pk=None):
        """
        Referee starts the match. Sets is_live=True and is_score_editable=True.
        """
        match = self.get_object()
        user = request.user
        
        is_referee = match.referee == user
        is_admin = user.is_staff
        
        if not (is_referee or is_admin):
            return Response({"detail": "Bu işlem için yetkiniz yok."}, status=status.HTTP_403_FORBIDDEN)
        
        if match.is_live:
            return Response({"detail": "Maç zaten başlamış."}, status=status.HTTP_400_BAD_REQUEST)
        
        if match.is_finished:
            return Response({"detail": "Maç zaten bitmiş."}, status=status.HTTP_400_BAD_REQUEST)
        
        match.is_live = True
        match.is_score_editable = True
        match.save(update_fields=['is_live', 'is_score_editable'])
        
        return Response({"detail": "Maç başlatıldı!"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def finish_match(self, request, pk=None):
        """
        Referee/Admin finishes the match.
        Triggers standing updates and enables rating.
        """
        match = self.get_object()
        user = request.user
        
        is_referee = match.referee == user
        is_admin = user.is_staff
        
        if not (is_referee):
            return Response({"detail": "Bu işlem için yetkiniz yok."}, status=status.HTTP_403_FORBIDDEN)
            
        if not match.is_score_editable:
             return Response({"detail": "Maç skoru düzenlemeye kapalı."}, status=status.HTTP_400_BAD_REQUEST)

        match.is_finished = True
        match.is_live = False
        match.is_score_editable = False # Lock editing
        match.finished_at = timezone.now()  # Set voting window start
        match.save() # Triggers _update_standings because is_finished became True
        
        return Response({"detail": "Maç bitirildi. Puan durumu güncellendi."})


@api_view(['GET'])
@permission_classes([AllowAny])
def recent_matches(request):
    """Get last 3 matches (home screen endpoint)"""
    matches = Match.objects.all().select_related('team1', 'team2').order_by('-date')[:3]
    serializer = MatchListSerializer(matches, many=True, context={'request': request})
    return Response(serializer.data)
