from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeagueViewSet, WeekViewSet, StandingViewSet

router = DefaultRouter()
router.register(r'weeks', WeekViewSet)
router.register(r'standings', StandingViewSet)
router.register(r'', LeagueViewSet) # Keep this last as it matches root

urlpatterns = [
    path('', include(router.urls)),
]
