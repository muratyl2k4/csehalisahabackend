from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Team
from .serializers import TeamListSerializer, TeamDetailSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Takımlar için ViewSet
    
    list: Tüm takımları listele
    retrieve: Tek bir takımın detaylarını getir
    """
    queryset = Team.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamListSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def top_teams(request):
    """En iyi 3 takımı getir (galibiyet sayısına göre)"""
    teams = Team.objects.all().order_by('-wins', '-losses')[:3]
    serializer = TeamListSerializer(teams, many=True, context={'request': request})
    return Response(serializer.data)
