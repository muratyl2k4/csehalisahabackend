from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from teams.models import Team


class Player(models.Model):
    """Oyuncu modeli"""
    current_team = models.ForeignKey(
        Team, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='players',
        verbose_name='Güncel Takım'
    )
    name = models.CharField(max_length=100, verbose_name='Oyuncu Adı')
    age = models.IntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(50)],
        verbose_name='Yaş'
    )
    photo = models.ImageField(
        upload_to='player_photos/', 
        verbose_name='Fotoğraf',
        blank=True,
        null=True
    )
    
    # FIFA stats (0-99)
    overall = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Overall',
        default=50
    )
    pace = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Hız (PAC)',
        default=50
    )
    shooting = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Şut (SHO)',
        default=50
    )
    passing = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Pas (PAS)',
        default=50
    )
    dribbling = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Dribling (DRI)',
        default=50
    )
    defense = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Defans (DEF)',
        default=50
    )
    physical = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        verbose_name='Fizik (PHY)',
        default=50
    )
    
    position = models.CharField(
        max_length=3,
        verbose_name='Pozisyon',
        default='ST',
        help_text='Örn: ST, LW, CM, CB'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    class Meta:
        verbose_name = 'Oyuncu'
        verbose_name_plural = 'Oyuncular'
        ordering = ['-overall', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.current_team.name if self.current_team else 'Takımsız'})"
    
    @property
    def total_goals(self):
        """Toplam gol sayısı"""
        from matches.models import PlayerMatchStats
        return PlayerMatchStats.objects.filter(player=self).aggregate(
            total=models.Sum('goals')
        )['total'] or 0
    
    @property
    def total_assists(self):
        """Toplam asist sayısı"""
        from matches.models import PlayerMatchStats
        return PlayerMatchStats.objects.filter(player=self).aggregate(
            total=models.Sum('assists')
        )['total'] or 0
    
    @property
    def matches_played(self):
        """Oynanan maç sayısı"""
        from matches.models import PlayerMatchStats
        return PlayerMatchStats.objects.filter(player=self, played=True).count()
