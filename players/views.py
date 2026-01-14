from rest_framework import viewsets, filters, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Player
from .serializers import (
    PlayerListSerializer,
    PlayerDetailSerializer,
    LeaderboardSerializer,
    PlayerRegisterSerializer,
    EmailTokenObtainPairSerializer,
    PlayerUpdateSerializer
)
from .pagination import PlayerPagination
from rest_framework.throttling import ScopedRateThrottle


class RegisterView(generics.CreateAPIView):
    queryset = Player.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = PlayerRegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    PlayerViewSet for players
    
    list: List all players
    retrieve: Retrieve a player's details
    """
    # queryset = Player.objects.all().select_related('current_team') # Moved to get_queryset
    permission_classes = [AllowAny]
    pagination_class = PlayerPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'current_team__name']
    filterset_fields = ['position']

    def get_permissions(self):
        """
        List and Retrieve are open to all.
        Create, Update, Destroy are only open to Admins.
        (Normal users manage their profiles using the 'me' endpoint)
        """ 
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        return [AllowAny()]

    
    def get_queryset(self):
        """
        List all players with teams and sort by overall.
        Show all players in detail.
        """
        qs = Player.objects.select_related('current_team').order_by('-overall')
        
        #Show only verified users
        if self.action == 'list':
            qs = qs.filter(is_email_verified=True)
        
        # if self.action == 'list':
        #     qs = qs.filter(current_team__isnull=False)
            
        return qs
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlayerDetailSerializer
        return PlayerListSerializer
    
    @action(detail=False, methods=['get'], url_path='leaderboard/goals')
    def goal_leaderboard(self, request):
        """
        Goal leaderboard
        GET /api/players/leaderboard/goals/
        """
        from matches.models import PlayerMatchStats
        
        players = Player.objects.annotate(
            total_goals=Sum('playermatchstats__goals')
        ).filter(total_goals__gt=0).order_by('-total_goals')

        serializer = LeaderboardSerializer(players, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='leaderboard/assists')
    def assist_leaderboard(self, request):
        """
        Assist leaderboard
        GET /api/players/leaderboard/assists/
        """

        players = Player.objects.annotate(
            total_assists=Sum('playermatchstats__assists')
        ).filter(
            total_assists__gt=0
        ).order_by('-total_assists')

        serializer = LeaderboardSerializer(
            players,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        """
        Get or update the current user's profile.
        GET /api/players/me/ -> Returns profile details
        PUT/PATCH /api/players/me/ -> Updates profile
        """
        try:
            player = getattr(request.user, 'player_profile', None)
            if not player:
                return Response(
                    {"detail": "Kullanıcıya ait oyuncu profili bulunamadı."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            if request.method == 'GET':
                serializer = PlayerDetailSerializer(player, context={'request': request})
                return Response(serializer.data)

            # PUT/PATCH
            serializer = PlayerUpdateSerializer(player, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                # Return updated full detail
                response_serializer = PlayerDetailSerializer(player, context={'request': request})
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    ##TODO Maybe move this to a different file and make a generic verification service.
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='verify-email')
    def verify_email(self, request):
        """
        E-mail verification endpoint.
        POST /api/players/verify-email/
        Body: { "email": "...", "code": "..." }
        """
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response(
                {"detail": "E-posta ve kod gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            player = Player.objects.get(user__email=email)
            
            # Check Expiration (15 minutes)
            if player.verification_code_created_at:
                from datetime import timedelta
                
                if timezone.now() - player.verification_code_created_at > timedelta(minutes=15):
                     return Response(
                        {"detail": "Doğrulama kodunun süresi dolmuş. Lütfen yeni kod isteyiniz."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if player.verification_code == code:
                player.is_email_verified = True
                player.verification_code = "" # Clear code after usage
                player.save()

                # Send Notification
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=player.user,
                    message="E-posta adresiniz başarıyla doğrulandı. Hesabınız artık aktif.",
                    notification_type='SYSTEM'
                )

                return Response({"detail": "E-posta başarıyla doğrulandı!"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Geçersiz doğrulama kodu."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Player.DoesNotExist:
            return Response(
                {"detail": "Kullanıcı bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='resend-code')
    def resend_verification_code(self, request):
        """
        Resend verification code
        POST /api/players/resend-code/
        Body: { "email": "..." }
        """
        import random
        from utils.email_service import EmailService

        email = request.data.get('email')
        if not email:
            return Response({"detail": "E-posta gereklidir."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            player = Player.objects.get(user__email=email)
            if player.is_email_verified:
                return Response({"detail": "Bu hesap zaten doğrulanmış."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check cooldown (60 seconds)
            if player.verification_code_created_at:
                from datetime import timedelta
                
                time_elapsed = timezone.now() - player.verification_code_created_at
                if time_elapsed < timedelta(seconds=60):
                    wait_seconds = 60 - int(time_elapsed.total_seconds())
                    return Response(
                        {"detail": f"Lütfen tekrar denemeden önce {wait_seconds} saniye bekleyiniz."}, 
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

            # Generate new code 
            new_code = str(random.randint(100000, 999999))
            player.verification_code = new_code
            player.verification_code_created_at = timezone.now()
            player.save()
            
            # Send Email
            EmailService.send_html(
                'Akdeniz CSE Halısaha - Yeni Doğrulama Kodu',
                'emails/verification.html',
                {'name': player.name, 'code': new_code},
                [email]
            )
            
            return Response({"detail": "Yeni doğrulama kodu gönderildi."}, status=status.HTTP_200_OK)
            
        except Player.DoesNotExist:
            return Response({"detail": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='verify-forgot-password-code')
    def verify_forgot_password_code(self, request):
        """
        Verify forgot password code
        POST /api/players/verify-forgot-password-code/
        Body: { "email": "...", "code": "..." }
        """
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"detail": "E-posta ve kod gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.get(user__email=email)
            
            # Verify Code match
            if player.verification_code != code:
                return Response({"detail": "Geçersiz doğrulama kodu."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify Expiration (15 minutes)
            if player.verification_code_created_at:
                from datetime import timedelta
                if timezone.now() - player.verification_code_created_at > timedelta(minutes=15):
                     return Response({"detail": "Kodun süresi dolmuş."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                 return Response({"detail": "Geçersiz işlem."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": "Kod doğrulandı."}, status=status.HTTP_200_OK)

        except Player.DoesNotExist:
             return Response({"detail": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='forgot-password')
    def forgot_password(self, request):
        """
        Send code for forgot password
        POST /api/players/forgot-password/
        Body: { "email": "..." }
        """
        import random
        from utils.email_service import EmailService

        email = request.data.get('email')
        if not email:
            return Response({"detail": "E-posta gereklidir."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            player = Player.objects.get(user__email=email)
            
            # Check cooldown (60 seconds)
            if player.verification_code_created_at:
                from datetime import timedelta
                time_elapsed = timezone.now() - player.verification_code_created_at
                if time_elapsed < timedelta(seconds=60):
                    wait_seconds = 60 - int(time_elapsed.total_seconds())
                    return Response(
                        {"detail": f"Lütfen {wait_seconds} saniye bekleyiniz."}, 
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

            # Generate new code and send email
            new_code = str(random.randint(100000, 999999))
            player.verification_code = new_code
            player.verification_code_created_at = timezone.now()
            player.save()
            
            EmailService.send_html(
                'Akdeniz CSE Halısaha - Şifre Sıfırlama Kodu',
                'emails/password_reset.html', 
                {'name': player.name, 'code': new_code},
                [email]
            )
            
            return Response({"detail": "Doğrulama kodu gönderildi."}, status=status.HTTP_200_OK)
            
        except Player.DoesNotExist:
            return Response({"detail": "Bu e-posta adresiyle kayıtlı kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='reset-password')
    def reset_password(self, request):
        """
        Completes Reset password.
        POST /api/players/reset-password/
        Body: { "email": "...", "code": "...", "new_password": "..." }
        """
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not email or not code or not new_password:
            return Response({"detail": "E-posta, kod ve yeni şifre gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = Player.objects.select_related('user').get(user__email=email)
            
            # Verify Code match
            if player.verification_code != code:
                return Response({"detail": "Geçersiz doğrulama kodu."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify Expiration
            if player.verification_code_created_at:
                from datetime import timedelta
                if timezone.now() - player.verification_code_created_at > timedelta(minutes=15):
                     return Response({"detail": "Kodun süresi dolmuş."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                 return Response({"detail": "Geçersiz işlem."}, status=status.HTTP_400_BAD_REQUEST)

            # Change Password and clean up
            user = player.user
            user.set_password(new_password)
            user.save()
            
            player.verification_code = "" # Invalidate code
            player.is_email_verified = True # Implicitly verify email if they own it enough to receive code
            player.save()


            # Send password changed notification
            from notifications.models import Notification
            Notification.objects.create(
                recipient=user,
                message="Şifreniz başarıyla değiştirildi. Güvenliğiniz için bu işlemi siz yapmadıysanız lütfen bizimle iletişime geçin.",
                notification_type='SYSTEM'
            )

            return Response({"detail": "Şifreniz başarıyla değiştirildi. Şimdi giriş yapabilirsiniz."}, status=status.HTTP_200_OK)

        except Player.DoesNotExist:
             return Response({"detail": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
