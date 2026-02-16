from django.db import models
from django.conf import settings
from teams.models import Team
from players.models import Player # Added import

class Match(models.Model):
    """Match Model"""
    date = models.DateTimeField(verbose_name='Maç Tarihi')
    # ... existing fields ...
    team1 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_matches',
        verbose_name='Takım 1'
    )
    team2 = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_matches',
        verbose_name='Takım 2'
    )
    team1_score = models.IntegerField(default=0, verbose_name='Takım 1 Skor')
    team2_score = models.IntegerField(default=0, verbose_name='Takım 2 Skor')
    is_finished = models.BooleanField(default=False, verbose_name='Maç Bitti mi?')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Zamanı')
    is_live = models.BooleanField(default=False, verbose_name='Canlı mı?')
    
    # Referee System
    referee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refereed_matches',
        verbose_name='Hakem'
    )
    is_score_editable = models.BooleanField(
        default=False, 
        verbose_name='Skor Girilebilir mi?',
        help_text='Hakem skoru ve istatistikleri düzenleyebilir mi?'
    )

    # New Architecture: Match linked to Week
    week = models.ForeignKey(
        'leagues.Week', 
        on_delete=models.CASCADE, 
        related_name='matches', 
        verbose_name='Hafta',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        verbose_name = 'Maç'
        verbose_name_plural = 'Maçlar'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.team1.name} {self.team1_score} - {self.team2_score} {self.team2.name}"
    
    @property
    def winner(self):
        # ... existing ...
        if not self.is_finished:
            return None
        if self.team1_score > self.team2_score:
            return self.team1
        elif self.team2_score > self.team1_score:
            return self.team2
        return None  # Beraberlik
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class PlayerMatchStats(models.Model):
    """Player's performance statistics in a match"""
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='player_stats',
        verbose_name='Maç'
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='match_stats',
        verbose_name='Oyuncu'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name='Oynadığı Takım',
        help_text='Oyuncunun bu maçta oynadığı takım (transfer geçmişi için)'
    )
    goals = models.IntegerField(default=0, verbose_name='Gol Sayısı')
    assists = models.IntegerField(default=0, verbose_name='Asist Sayısı')
    
    # Card Stats
    yellow_cards = models.IntegerField(default=0, verbose_name='Sarı Kart')
    red_cards = models.IntegerField(default=0, verbose_name='Kırmızı Kart')
    
    played = models.BooleanField(default=True, verbose_name='Oynadı mı?')
    
    class Meta:
        verbose_name = 'Oyuncu Maç İstatistiği'
        verbose_name_plural = 'Oyuncu Maç İstatistikleri'
        unique_together = ['match', 'player'] 
        ordering = ['-match__date']
    

class PlayerMatchRating(models.Model):
    """
    Peer review ratings for a match.
    Players rate opponents on a scale of 1-10.
    These ratings are normalized to 75-99 for the overall score.
    """
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Maç'
    )
    rater = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='given_ratings',
        verbose_name='Oylayan'
    )
    rated_player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='received_ratings',
        verbose_name='Oylanan'
    )
    
    # Attributes (1-10)
    rating_pace = models.IntegerField(default=5, verbose_name='Hız (PAC)')
    rating_shooting = models.IntegerField(default=5, verbose_name='Şut (SHO)')
    rating_passing = models.IntegerField(default=5, verbose_name='Pas (PAS)')
    rating_dribbling = models.IntegerField(default=5, verbose_name='Top Sürme (DRI)')
    rating_defense = models.IntegerField(default=5, verbose_name='Defans (DEF)')
    rating_physical = models.IntegerField(default=5, verbose_name='Fizik (PHY)')
    
    # GK Attributes (1-10)
    rating_diving = models.IntegerField(default=5, verbose_name='Uçma (DIV)')
    rating_handling = models.IntegerField(default=5, verbose_name='Elle Kontrol (HAN)')
    rating_kicking = models.IntegerField(default=5, verbose_name='Ayak (KIC)')
    rating_reflexes = models.IntegerField(default=5, verbose_name='Refleks (REF)')
    rating_speed = models.IntegerField(default=5, verbose_name='Hız (SPD)')
    rating_positioning = models.IntegerField(default=5, verbose_name='Yer Tutma (POS)')
    
    comment = models.TextField(blank=True, null=True, verbose_name='Yorum')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Oyuncu Değerlendirmesi'
        verbose_name_plural = 'Oyuncu Değerlendirmeleri'
        unique_together = ['match', 'rater', 'rated_player']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rater.name} -> {self.rated_player.name} ({self.match})"

    @property
    def average_score_10(self):
        """Average of the 6 attributes on 1-10 scale"""
        total = (
            self.rating_pace + self.rating_shooting + 
            self.rating_passing + self.rating_dribbling + 
            self.rating_defense + self.rating_physical
        )
        return total / 6

    @property
    def normalized_score(self):
        """
        Maps 1-10 scale to 75-99 scale.
        Formula: 75 + ((Avg - 1) * (24/9))
        """
        avg = self.average_score_10
        if avg < 1: avg = 1
        if avg > 10: avg = 10
        
        return 75 + ((avg - 1) * (24/9))

