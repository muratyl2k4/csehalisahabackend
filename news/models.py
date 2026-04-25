import os
import uuid
from django.db import models
from django.contrib.auth.models import User

def secure_news_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('news_photos/', filename)

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='Başlık')
    content = models.TextField(verbose_name='Açıklama')
    photo = models.ImageField(upload_to='news_photos/', blank=True, null=True, verbose_name='Fotoğraf')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='news', verbose_name='Yazar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')

    class Meta:
        verbose_name = 'Haber'
        verbose_name_plural = 'Haberler'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
