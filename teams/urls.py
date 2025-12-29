from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, top_teams

router = DefaultRouter()
router.register(r'', TeamViewSet, basename='team')

urlpatterns = [
    path('top/', top_teams, name='top-teams'),
    path('', include(router.urls)),
]
