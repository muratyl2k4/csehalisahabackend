from django.db import models



class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name='Takım Adı', unique=True)
    short_name = models.CharField(max_length=5, verbose_name='Kısaltma', blank=True, null=True)
    logo = models.ImageField(upload_to='team_logos/', verbose_name='Takım Logosu', blank=True, null=True)
    wins = models.IntegerField(default=0, verbose_name='Kazanılan Maçlar')
    draws = models.IntegerField(default=0, verbose_name='Beraberlikler')
    losses = models.IntegerField(default=0, verbose_name='Kaybedilen Maçlar')
    goals_scored = models.IntegerField(default=0, verbose_name='Atılan Goller')
    goals_conceded = models.IntegerField(default=0, verbose_name='Yenen Goller')
    points = models.IntegerField(default=0, verbose_name='Puan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    captain = models.ForeignKey('players.Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='captain_of', verbose_name='Kaptan')
    
    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        ordering = ['-points', '-goals_scored', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_matches(self):
        return self.wins + self.draws + self.losses
    
    @property
    def win_rate(self):
        if self.total_matches == 0:
            return 0
        return round((self.wins / self.total_matches) * 100, 1)
    
    @property
    def goal_difference(self):
        return self.goals_scored - self.goals_conceded

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class TransferRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Bekliyor'),
        ('ACCEPTED', 'Kabul Edildi'),
        ('REJECTED', 'Reddedildi'),
    )
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='transfer_requests', verbose_name='Oyuncu')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='transfer_requests', verbose_name='Takım')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Durum')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tarih')

    class Meta:
        verbose_name = 'Transfer İsteği'
        verbose_name_plural = 'Transfer İstekleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player.name} -> {self.team.name} ({self.get_status_display()})"
