from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Team, TransferRequest
from .serializers import TeamListSerializer, TeamDetailSerializer, TeamCreateSerializer, TeamUpdateSerializer, TransferRequestSerializer


class TeamViewSet(viewsets.ModelViewSet):
    """
    TeamViewSet
    
    list: List all teams
    create: Create a new team (Only users without a team)
    retrieve: Get team details
    join: Send join request to team
    """
    def get_queryset(self):
        qs = Team.objects.all().select_related('captain')
        return qs
    
    def get_permissions(self):
        if self.action in ['create', 'join', 'leave', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    

    '''
    !!Object-Level Authorization!!
    This overrides the default update method to ensure only the captain of the team can update it.
    if we change the code without getting instance of the team, any captain user can update any team.
    but this way is not the best way to do it.
    we can use permissions to do it.
    
    '''
    def update(self, request, *args, **kwargs):
        # Override update to ensure only captain can update
        instance = self.get_object()
        player = getattr(request.user, 'player_profile', None)
        if not player or instance.captain != player:
             return Response({'detail': 'Sadece takım kaptanı güncelleme yapabilir.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Override destroy to ensure only captain can delete
        instance = self.get_object()
        player = getattr(request.user, 'player_profile', None)
        if not player or instance.captain != player:
             return Response({'detail': 'Sadece takım kaptanı takımı silebilir.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Override partial_update to ensure only captain can update
        instance = self.get_object()
        player = getattr(request.user, 'player_profile', None)
        if not player or instance.captain != player:
             return Response({'detail': 'Sadece takım kaptanı güncelleme yapabilir.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        if self.action == 'create':
            return TeamCreateSerializer
        if self.action in ['update', 'partial_update']:
             return TeamUpdateSerializer
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
        """Send join request to team"""
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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request):
        """Leave team"""
        user = request.user
        if not hasattr(user, 'player_profile'):
            return Response({'detail': 'Oyuncu profili bulunamadı.'}, status=400)
            
        player = user.player_profile
        team = player.current_team
        
        if not team:
             return Response({'detail': 'Herhangi bir takımda değilsiniz.'}, status=400)
             
        # Check if Captain
        if team.captain == player:
            return Response({'detail': 'Takım kaptanı takımdan ayrılamaz. Önce kaptanlığı devredin veya takımı silin.'}, status=400)
            
        # Leave
        player.current_team = None
        player.save()
        
        return Response({'detail': 'Takımdan başarıyla ayrıldınız.'}, status=200)

##TODO queryset filter by user's team, user should only see his team's transfer requests
##Make IsTargetTeamCaptain permission
class TransferRequestViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin):
    queryset = TransferRequest.objects.all()
    serializer_class = TransferRequestSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to transfer request (ACCEPT / REJECT)"""
        transfer_request = self.get_object()
        action = request.data.get('action') # 'ACCEPT' or 'REJECT'
        
        # Check permissions: Request user must be the CAPTAIN of the target team
        if not hasattr(request.user, 'player_profile'):
             return Response({'detail': 'Yetkisiz işlem.'}, status=403)
             
        captain = request.user.player_profile
        if transfer_request.team.captain != captain:
            return Response({'detail': 'Bu isteği yönetmek için takım kaptanı olmalısınız.'}, status=403)
            
        if transfer_request.status != 'PENDING':
            return Response({'detail': 'Bu istek zaten işlenmiş.'}, status=400)
            
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
    """Get top 3 teams (by wins)"""
    teams = Team.objects.all().order_by('-wins', '-losses')[:3]
    serializer = TeamListSerializer(teams, many=True, context={'request': request})
    return Response(serializer.data)
