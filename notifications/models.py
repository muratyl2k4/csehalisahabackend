from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPE_CHOICES = (
        ('TEAM_REQUEST', 'Takım İsteği'),
        ('TEAM_RESPONSE', 'Takım Yanıtı'),
        ('SYSTEM', 'Sistem Mesajı'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Alıcı')
    title = models.CharField(max_length=255, default='Yeni Bildirim', verbose_name='Başlık')
    message = models.TextField(verbose_name='Mesaj')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM', verbose_name='Bildirim Tipi')
    is_read = models.BooleanField(default=False, verbose_name='Okundu mu?')
    related_link = models.CharField(max_length=255, blank=True, null=True, verbose_name='İlgili Link')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tarih')

    class Meta:
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.get_notification_type_display()}"
