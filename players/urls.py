from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PlayerViewSet, RegisterView, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'', PlayerViewSet, basename='player')

urlpatterns = [
    path('', include(router.urls)),
]
