from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import League, Week, Standing
from .serializers import LeagueSerializer, WeekSerializer, StandingSerializer

class LeagueViewSet(viewsets.ModelViewSet):
    """
    LeagueViewSet
    
    list: List all leagues
    retrieve: Get specific league
    """
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

class WeekViewSet(viewsets.ModelViewSet):
    """
    WeekViewSet
    
    list: List all weeks
    retrieve: Get specific week
    filterset_fields: league
    """
    queryset = Week.objects.all().order_by('start_date', 'name')
    serializer_class = WeekSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['league']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
             return [AllowAny()]
        return [IsAdminUser()]

class StandingViewSet(viewsets.ModelViewSet):
    """
    StandingViewSet
    
    list: List all standings
    retrieve: Get specific standing
    filterset_fields: league, team
    """
    queryset = Standing.objects.all().select_related('team').order_by('-points', '-goals_for')
    serializer_class = StandingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['league', 'team']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
