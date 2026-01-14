from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TransferRequestViewSet, top_teams

router = DefaultRouter()
router.register(r'requests', TransferRequestViewSet, basename='transfer-request')
router.register(r'', TeamViewSet, basename='team')

urlpatterns = [
    path('top/', top_teams, name='top-teams'),
    path('', include(router.urls)),
]
