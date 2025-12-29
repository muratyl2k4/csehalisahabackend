from django.db import models
from teams.models import Team
from players.models import Player


class Match(models.Model):
    """Maç modeli"""
    date = models.DateTimeField(verbose_name='Maç Tarihi')
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        verbose_name = 'Maç'
        verbose_name_plural = 'Maçlar'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.team1.name} {self.team1_score} - {self.team2_score} {self.team2.name}"
    
    @property
    def winner(self):
        """Kazanan takımı döndür"""
        if not self.is_finished:
            return None
        if self.team1_score > self.team2_score:
            return self.team1
        elif self.team2_score > self.team1_score:
            return self.team2
        return None  # Beraberlik
    
    def save(self, *args, **kwargs):
        """Maç bittiğinde takım istatistiklerini güncelle"""
        is_new = self.pk is None
        old_match = None
        
        if not is_new:
            old_match = Match.objects.get(pk=self.pk)
        
        super().save(*args, **kwargs)
        
        # Eğer maç yeni bitiyorsa veya skor değiştiyse takım stats güncelle
        if self.is_finished:
            if is_new or (old_match and not old_match.is_finished):
                self._update_team_stats()
            elif old_match and (old_match.team1_score != self.team1_score or old_match.team2_score != self.team2_score):
                # Eski skorları geri al
                self._revert_team_stats(old_match)
                # Yeni skorları uygula
                self._update_team_stats()
    
    def _update_team_stats(self):
        """Takım istatistiklerini güncelle"""
        if self.team1_score > self.team2_score:
            self.team1.wins += 1
            self.team2.losses += 1
        elif self.team2_score > self.team1_score:
            self.team2.wins += 1
            self.team1.losses += 1
        # Beraberlik durumunda kazanma/kaybetme sayısı değişmez
        
        self.team1.save()
        self.team2.save()
    
    def _revert_team_stats(self, old_match):
        """Eski maç sonucunu geri al"""
        if old_match.team1_score > old_match.team2_score:
            self.team1.wins -= 1
            self.team2.losses -= 1
        elif old_match.team2_score > old_match.team1_score:
            self.team2.wins -= 1
            self.team1.losses -= 1
        
        self.team1.save()
        self.team2.save()


class PlayerMatchStats(models.Model):
    """Oyuncunun bir maçtaki performans istatistikleri"""
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
    played = models.BooleanField(default=True, verbose_name='Oynadı mı?')
    
    class Meta:
        verbose_name = 'Oyuncu Maç İstatistiği'
        verbose_name_plural = 'Oyuncu Maç İstatistikleri'
        unique_together = ['match', 'player']  # Bir oyuncu bir maçta bir kere oynar
        ordering = ['-match__date']
    
    def __str__(self):
        return f"{self.player.name} - {self.match} ({self.goals}G, {self.assists}A)"
