from django.db import models
from teams.models import Team
from players.models import Player


class Match(models.Model):
    """Match Model"""
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
        """Update team statistics when match is finished"""
        is_new = self.pk is None
        old_match = None
        
        if not is_new:
            old_match = Match.objects.get(pk=self.pk)
        
        super().save(*args, **kwargs)
        
        # If the match is finished, update team statistics
        if self.is_finished:
            if is_new or (old_match and not old_match.is_finished):
                self._update_team_stats()
            elif old_match and (old_match.team1_score != self.team1_score or old_match.team2_score != self.team2_score):
                # Revert old scores
                self._revert_team_stats(old_match)
                # Apply new scores
                self._update_team_stats()
    
    def _update_team_stats(self):
        """Update team statistics (Points, G, B, M, Goals)"""
        # Process goals
        self.team1.goals_scored += self.team1_score
        self.team1.goals_conceded += self.team2_score
        self.team2.goals_scored += self.team2_score
        self.team2.goals_conceded += self.team1_score
        
        # Process result
        if self.team1_score > self.team2_score:
            self.team1.wins += 1
            self.team1.points += 3
            self.team2.losses += 1
        elif self.team2_score > self.team1_score:
            self.team2.wins += 1
            self.team2.points += 3
            self.team1.losses += 1
        else:
            self.team1.draws += 1
            self.team1.points += 1
            self.team2.draws += 1
            self.team2.points += 1
        
        self.team1.save()
        self.team2.save()
    
    def _revert_team_stats(self, old_match):
        """Revert old match result"""
        # Revert goals
        self.team1.goals_scored -= old_match.team1_score
        self.team1.goals_conceded -= old_match.team2_score
        self.team2.goals_scored -= old_match.team2_score
        self.team2.goals_conceded -= old_match.team1_score
        
        # Revert result
        if old_match.team1_score > old_match.team2_score:
            self.team1.wins -= 1
            self.team1.points -= 3
            self.team2.losses -= 1
        elif old_match.team2_score > old_match.team1_score:
            self.team2.wins -= 1
            self.team2.points -= 3
            self.team1.losses -= 1
        else:
            self.team1.draws -= 1
            self.team1.points -= 1
            self.team2.draws -= 1
            self.team2.points -= 1
        
        self.team1.save()
        self.team2.save()


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
    played = models.BooleanField(default=True, verbose_name='Oynadı mı?')
    
    class Meta:
        verbose_name = 'Oyuncu Maç İstatistiği'
        verbose_name_plural = 'Oyuncu Maç İstatistikleri'
        unique_together = ['match', 'player']  # Bir oyuncu bir maçta bir kere oynar TODO bir oyuncu zaten iki farkli takimda oynayamayacak sekilde duzenlenecek.!
        ordering = ['-match__date']
    
    def __str__(self):
        return f"{self.player.name} - {self.match} ({self.goals}G, {self.assists}A)"
