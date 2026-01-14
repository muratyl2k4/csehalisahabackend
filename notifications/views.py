from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from core.permissions import IsReadOnly

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notification list and mark as read operations.
    Only read (list/retrieve) and custom actions are available.
    """
    serializer_class = NotificationSerializer

    def get_permissions(self):
        """
        Özel aksiyonlar için izinleri ayarla.
        """
        if self.action == 'register_subscription':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'broadcast':
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['mark_read', 'mark_all_read', 'unread_count', 'save_push_info']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            # list, retrieve, destroy vb.
            permission_classes = [permissions.IsAuthenticated, (permissions.IsAdminUser | IsReadOnly)]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def broadcast(self, request):
        """
        Broadcast Notification (Admin).
        Modes:
        - target='all': Send to all devices (Anonymous + Registered).
        - target='users': Send to registered users only (PushInformation).
        In both cases, registered users' Inbox is updated.
        """
        from webpush.models import SubscriptionInfo, PushInformation
        
        message = request.data.get('message')
        title = request.data.get('title', 'Duyuru')
        target = request.data.get('target', 'users') # 'all' or 'users'
        
        if not message:
            return Response({"detail": "Mesaj içeriği gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Target Selection
        subscriptions = []
        target_users_for_db = []

        if target == 'all':
            # Send to all (Anonymous + Registered)
            subscriptions = SubscriptionInfo.objects.all()
            from django.contrib.auth.models import User
            target_users_for_db = User.objects.all()
        elif target == 'single':
            # Send to single user
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
            # Send to registered users only (Default)
            subscriptions = [pi.subscription for pi in PushInformation.objects.select_related('subscription').all()]
            from django.contrib.auth.models import User
            target_users_for_db = User.objects.all()

        import json
        payload = json.dumps({
            "title": title,
            "body": message,
            "icon": "/logo1.png",
            "url": "/"
        })

        # 2. DB Record (Inbox)
        notifications = [
            Notification(
                recipient=user,
                title=title,
                message=message,
                notification_type='SYSTEM'
            ) for user in target_users_for_db
        ]
        Notification.objects.bulk_create(notifications)

        # 3. PUSH Notification
        from pywebpush import webpush
        import sys 

        print(f"DEBUG: Starting Broadcast to {len(subscriptions)} subs...", file=sys.stdout, flush=True)
        
        success_count = 0
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {
                            "auth": sub.auth,
                            "p256dh": sub.p256dh
                        }
                    },
                    data=payload,
                    vapid_private_key="vokzWx36wRxAC1BWWVKskRwR1QzhxRGkvEixejFa1zI",
                    vapid_claims={"sub": "mailto:akdenizcselig@gmail.com"},
                    ttl=60
                )
                success_count += 1
            except Exception as e:
                print(f"=======Push Error for {sub.endpoint[:20]}...", file=sys.stdout, flush=True)
                print(f"=======Error: {str(e)}", file=sys.stdout, flush=True)
                if hasattr(e, 'response') and e.response:
                    try:
                        print(f"   Response: {e.response.text}", file=sys.stdout, flush=True)
                    except:
                        pass
                pass

        return Response({
            "detail": f"Bildirim gönderildi. ({success_count}/{len(subscriptions)} Başarılı)"
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request, pk=None):
        """Mark all notifications as read"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})

    @action(detail=False, methods=['post'])
    def save_push_info(self, request):
        """
        WebPush subscription info (JWT compatible).
        """
        pass

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register_subscription(self, request):
        """
        Simplified Subscription Registration.
        Registers both logged-in and anonymous devices.
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
            
            # User insisted on user_agent being here.
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
            # Catching attribute errors if user_agent doesn't exist to prevent full fatal crash
            if "user_agent" in str(e):
                 return Response({"detail": "Model error: user_agent mismatch. Contact admin."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
