from django.db import models


class Team(models.Model):
    """Takım modeli"""
    name = models.CharField(max_length=100, verbose_name='Takım Adı', unique=True)
    short_name = models.CharField(max_length=5, verbose_name='Kısaltma', blank=True, null=True)
    logo = models.ImageField(upload_to='team_logos/', verbose_name='Takım Logosu', blank=True, null=True)
    wins = models.IntegerField(default=0, verbose_name='Kazanılan Maçlar')
    losses = models.IntegerField(default=0, verbose_name='Kaybedilen Maçlar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        ordering = ['-wins', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_matches(self):
        """Toplam oynanan maç sayısı"""
        return self.wins + self.losses
    
    @property
    def win_rate(self):
        """Kazanma oranı (yüzde)"""
        if self.total_matches == 0:
            return 0
        return round((self.wins / self.total_matches) * 100, 1)
    
    @property
    def draws(self):
        """Berabere kalan maçlar - matches modelinden hesaplanacak"""
        from matches.models import Match
        draws = Match.objects.filter(
            models.Q(team1=self, team1_score=models.F('team2_score')) |
            models.Q(team2=self, team1_score=models.F('team2_score')),
            is_finished=True
        ).count()
        return draws
