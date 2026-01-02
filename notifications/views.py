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
        Tüm kullanıcılara bildirim gönderir (Sadece Admin).
        POST /api/notifications/broadcast/
        Body: { "message": "..." }
        """
        message = request.data.get('message')
        if not message:
            return Response({"detail": "Mesaj içeriği gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth.models import User
        users = User.objects.all()
        
        notifications = [
            Notification(
                recipient=user,
                message=message,
                notification_type='SYSTEM'
            ) for user in users
        ]
        
        Notification.objects.bulk_create(notifications)
        
        return Response({"detail": f"{len(notifications)} kullanıcıya bildirim gönderildi."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Tüm bildirimleri okundu işaretle"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})
