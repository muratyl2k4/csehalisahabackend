from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MatchViewSet, recent_matches

router = DefaultRouter()
router.register(r'', MatchViewSet, basename='match')

urlpatterns = [
    path('recent/', recent_matches, name='recent-matches'),
    path('', include(router.urls)),
]
