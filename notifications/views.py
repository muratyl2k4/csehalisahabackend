from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from core.permissions import IsReadOnly

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Bildirimleri listeleme ve okundu işaretleme işlemleri.
    Sadece okuma (list/retrieve) ve özel aksiyonlar var.
    """

    serializer_class = NotificationSerializer
    serializer_class = NotificationSerializer
    # Remove class-level permission_classes to use get_permissions
    # permission_classes = [permissions.IsAuthenticated, (permissions.IsAdminUser | IsReadOnly)]

    def get_permissions(self):
        """
        Özel aksiyonlar (mark_read, mark_all_read) için sadece giriş yapmış olmak yeterli.
        Diğer işlemler (create, update, delete) için Admin veya ReadOnly gerekli.
        """
        if self.action in ['mark_read', 'mark_all_read', 'unread_count']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, (permissions.IsAdminUser | IsReadOnly)]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Bildirimi okundu olarak işaretle"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Okunmamış bildirim sayısını döner"""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def broadcast(self, request):
        """
        Bildirim Gönderme (Admin).
        Modes:
        - target='all': Tüm Cihazlara (Anonim + Kayıtlı) gönderir.
        - target='users': Sadece Kayıtlı Kullanıcılara (PushInformation) gönderir.
        Her iki durumda da kayıtlı kullanıcıların Inbox'ına eklenir.
        """
        from webpush.models import SubscriptionInfo, PushInformation
        from webpush.utils import send_to_subscription
        
        message = request.data.get('message')
        title = request.data.get('title', 'Duyuru')
        target = request.data.get('target', 'users') # 'all' or 'users'
        
        if not message:
            return Response({"detail": "Mesaj içeriği gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. PUSH Gönderimi
        # 1. PUSH Gönderimi
        subscriptions = []
        target_users_for_db = []

        if target == 'all':
            # Herkese (Anonim dahil)
            subscriptions = SubscriptionInfo.objects.all()
            from django.contrib.auth.models import User
            target_users_for_db = User.objects.all()
        elif target == 'single':
            # Tek Kullanıcıya
            username = request.data.get('username')
            if not username:
                return Response({"detail": "target='single' için 'username' gereklidir."}, status=status.HTTP_400_BAD_REQUEST)
            
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username=username)
                subscriptions = [pi.subscription for pi in PushInformation.objects.filter(user=user).select_related('subscription')]
                target_users_for_db = [user]
            except User.DoesNotExist:
                return Response({"detail": f"Kullanıcı bulunamadı: {username}"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Sadece Kayıtlı Kullanıcılara (Default)
            subscriptions = [pi.subscription for pi in PushInformation.objects.select_related('subscription').all()]
            from django.contrib.auth.models import User
            target_users_for_db = User.objects.all()

        s_count = 0
        import json
        payload = json.dumps({
            "title": title,
            "body": message,
            "icon": "/logo1.png",
            "url": "/"
        })

        # Tekrar eden subscriptionları önlemek için set kullanılabilir ama SubscriptionInfo unique ise gerek yok.
        # Basit döngü:
        # Basit döngü:
        errors = []
        for sub in subscriptions:
            try:
                # iOS için ttl=60 (kısa tutmak bazen iyidir) ve urgency gerekebilir ama varsayılan genellikle çalışır.
                send_to_subscription(sub, payload, ttl=86400)
                s_count += 1
            except Exception as e:
                # Hata detayını kaydet
                error_msg = f"Device {sub.pk} Error: {str(e)}"
                print(error_msg)
                errors.append(error_msg)

        # 2. DB Kaydı (Inbox)
        notifications = [
            Notification(
                recipient=user,
                title=title,
                message=message,
                notification_type='SYSTEM'
            ) for user in target_users_for_db
        ]
        
        Notification.objects.bulk_create(notifications)
        
        response_detail = f"Mod: {target} | Hedef: {username if target == 'single' else 'Toplu'} | " \
                          f"{s_count} Push Gönderildi | {len(notifications)} DB Kaydı."
        if errors:
            response_detail += f" Hatalar: {str(errors[:3])}"

        return Response({
            "detail": response_detail
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Tüm bildirimleri okundu işaretle"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})

    @action(detail=False, methods=['post'])
    def save_push_info(self, request):
        """
        WebPush abonelik bilgisini kaydeder (JWT uyumlu).
        """
        from webpush.models import PushInformation

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register_subscription(self, request):
        """
        Basitleştirilmiş Abonelik Kaydı.
        Hem giriş yapmış hem anonim (ileride gerekirse) cihazları kaydeder.
        """
        from webpush.models import PushInformation, SubscriptionInfo
        
        subscription_data = request.data.get('subscription')
        browser = request.data.get('browser', 'Unknown')

        if not subscription_data:
            return Response({"detail": "No subscription data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Cihaz/Tarayıcı Aboneliğini Kaydet (SubscriptionInfo)
            endpoint = subscription_data.get('endpoint')
            keys = subscription_data.get('keys', {})
            
            subscription_info, created = SubscriptionInfo.objects.get_or_create(
                endpoint=endpoint,
                defaults={
                    "auth": keys.get('auth'),
                    "p256dh": keys.get('p256dh'),
                    "browser": browser,
                    "user_agent": request.META.get('HTTP_USER_AGENT', '')
                }
            )

            # 2. Eğer kullanıcı giriş yapmışsa, bu cihazı kullanıcıyla eşleştir (PushInformation)
            if request.user.is_authenticated:
                PushInformation.objects.get_or_create(
                    user=request.user,
                    subscription=subscription_info,
                    defaults={}
                )
            
            return Response({"status": "registered", "user": request.user.username}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
