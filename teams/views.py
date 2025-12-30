from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Team, TransferRequest
from .serializers import TeamListSerializer, TeamDetailSerializer, TeamCreateSerializer, TransferRequestSerializer


class TeamViewSet(viewsets.ModelViewSet):
    """
    Takımlar için ViewSet
    
    list: Tüm takımları listele
    create: Yeni takım oluştur (Sadece takımı olmayan kullanıcılar)
    retrieve: Tek bir takımın detaylarını getir
    join: Takıma katılma isteği gönder
    """
    queryset = Team.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'join']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        if self.action == 'create':
            return TeamCreateSerializer
        return TeamListSerializer

    def create(self, request, *args, **kwargs):
        # 1. Check if user has a profile
        if not hasattr(request.user, 'player_profile'):
            return Response({'detail': 'Oyuncu profili bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)
        
        player = request.user.player_profile
        
        # 2. Check if player is already in a team
        if player.current_team:
            return Response({'detail': 'Zaten bir takımınız var. Yeni takım oluşturamazsınız.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 3. Create Team
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 3.1 Assign create as captain
        team = serializer.save(captain=player) 
        
        # 4. Assign Player to Team
        player.current_team = team
        player.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """Takıma katılma isteği gönder"""
        team = self.get_object()
        user = request.user
        
        if not hasattr(user, 'player_profile'):
            return Response({'detail': 'Oyuncu profiliniz yok.'}, status=400)
            
        player = user.player_profile
        
        if player.current_team:
            return Response({'detail': 'Zaten bir takımınız var.'}, status=400)
            
        # Check existing PENDING request
        if TransferRequest.objects.filter(player=player, team=team, status='PENDING').exists():
             return Response({'detail': 'Bu takıma zaten bekleyen bir isteğiniz var.'}, status=400)
             
        TransferRequest.objects.create(player=player, team=team)
        return Response({'detail': 'Katılma isteği gönderildi.'}, status=200)


class TransferRequestViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin):
    queryset = TransferRequest.objects.all()
    serializer_class = TransferRequestSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """İsteğe yanıt ver (ACCEPT / REJECT)"""
        transfer_request = self.get_object()
        action = request.data.get('action') # 'ACCEPT' or 'REJECT'
        
        # Check permissions: Request user must be the CAPTAIN of the target team
        if not hasattr(request.user, 'player_profile'):
             return Response({'detail': 'Yetkisiz işlem.'}, status=403)
             
        captain = request.user.player_profile
        if transfer_request.team.captain != captain:
            return Response({'detail': 'Bu isteği yönetmek için takım kaptanı olmalısınız.'}, status=403)
            
        if action == 'ACCEPT':
            # Check if player joined another team in the meantime
            if transfer_request.player.current_team:
                transfer_request.status = 'REJECTED'
                transfer_request.save()
                return Response({'detail': 'Oyuncu zaten başka bir takıma girmiş.'}, status=400)
                
            transfer_request.status = 'ACCEPTED'
            transfer_request.save()
            
            # Add player to team
            player = transfer_request.player
            player.current_team = transfer_request.team
            player.save()
            return Response({'detail': 'Oyuncu takıma kabul edildi.'})
            
        elif action == 'REJECT':
            transfer_request.status = 'REJECTED'
            transfer_request.save()
            return Response({'detail': 'İstek reddedildi.'})
            
        return Response({'detail': 'Geçersiz işlem.'}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def top_teams(request):
    """En iyi 3 takımı getir (galibiyet sayısına göre)"""
    teams = Team.objects.all().order_by('-wins', '-losses')[:3]
    serializer = TeamListSerializer(teams, many=True, context={'request': request})
    return Response(serializer.data)
