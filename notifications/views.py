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
        subscriptions = []
        if target == 'all':
            # Herkese (Anonim dahil)
            subscriptions = SubscriptionInfo.objects.all()
        else:
            # Sadece Kayıtlı Kullanıcılara
            subscriptions = [pi.subscription for pi in PushInformation.objects.select_related('subscription').all()]

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
        for sub in subscriptions:
            try:
                send_to_subscription(sub, payload, ttl=1000)
                s_count += 1
            except Exception as e:
                print(f"Push Error for {sub.pk}: {e}")
                pass

        # 2. DB Kaydı (Inbox) - Her zaman kayıtlı kullanıcılara ekle
        from django.contrib.auth.models import User
        users = User.objects.all()
        
        notifications = [
            Notification(
                recipient=user,
                title=title,
                message=message,
                notification_type='SYSTEM'
            ) for user in users
        ]
        
        Notification.objects.bulk_create(notifications)
        
        return Response({
            "detail": f"{s_count} cihaza push gönderildi ({target}), {len(notifications)} kullanıcının kutusuna eklendi."
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
