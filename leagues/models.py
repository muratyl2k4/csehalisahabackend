from django.db import models

class League(models.Model):
    """Lig Modeli"""
    name = models.CharField(max_length=100, verbose_name='Lig Adı')
    season = models.CharField(max_length=50, verbose_name='Sezon', help_text="Örn: 2024-2025")
    is_active = models.BooleanField(default=True, verbose_name='Aktif Lig')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')

    class Meta:
        verbose_name = 'Lig'
        verbose_name_plural = 'Ligler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.season})"

class Week(models.Model):
    """Lig Haftası (Örn: 1. Hafta)"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='weeks', verbose_name='Lig')
    name = models.CharField(max_length=50, verbose_name='Hafta Adı') # Örn: "1. Hafta"
    start_date = models.DateField(null=True, blank=True, verbose_name='Başlangıç Tarihi')
    end_date = models.DateField(null=True, blank=True, verbose_name='Bitiş Tarihi')
    is_played = models.BooleanField(default=False, verbose_name='Oynandı mı?')

    class Meta:
        verbose_name = 'Hafta'
        verbose_name_plural = 'Haftalar'
        ordering = ['league', 'start_date', 'name']

    def __str__(self):
        return f"{self.name} ({self.league})"

class Standing(models.Model):
    """Puan Durumu Tablosu (Bir takımın bir ligdeki performansı)"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='standings', verbose_name='Lig')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='league_standings', verbose_name='Takım')
    
    played = models.IntegerField(default=0, verbose_name='Oynanan')
    wins = models.IntegerField(default=0, verbose_name='Galibiyet')
    draws = models.IntegerField(default=0, verbose_name='Beraberlik')
    losses = models.IntegerField(default=0, verbose_name='Mağlubiyet')
    goals_for = models.IntegerField(default=0, verbose_name='Atılan Gol')
    goals_against = models.IntegerField(default=0, verbose_name='Yenen Gol')
    points = models.IntegerField(default=0, verbose_name='Puan')

    class Meta:
        verbose_name = 'Puan Durumu'
        verbose_name_plural = 'Puan Durumları'
        unique_together = ['league', 'team'] # Bir takım bir ligde sadece bir kere yer alabilir
        ordering = ['-points', '-goals_for']

    def __str__(self):
        return f"{self.team.name} - {self.league.name}"
    
    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

