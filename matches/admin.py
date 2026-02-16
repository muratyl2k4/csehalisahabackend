from django.contrib import admin
from .models import Match, PlayerMatchStats, PlayerMatchRating


@admin.register(PlayerMatchRating)
class PlayerMatchRatingAdmin(admin.ModelAdmin):
    list_display = ['match', 'rater', 'rated_player', 'rating_pace', 'rating_shooting', 'rating_passing', 'rating_defense', 'created_at']
    list_filter = ['match', 'rater', 'rated_player', 'created_at']
    search_fields = ['rater__name', 'rated_player__name', 'match__team1__name', 'match__team2__name']
    
    fieldsets = (
        ('Oylama Bilgisi', {
            'fields': ('match', 'rater', 'rated_player')
        }),
        ('Puanlar', {
            'fields': ('rating_pace', 'rating_shooting', 'rating_passing', 'rating_dribbling', 'rating_defense', 'rating_physical')
        }),
        ('Yorum', {
            'fields': ('comment',)
        }),
    )


class PlayerMatchStatsInline(admin.TabularInline):
    """Player Match Stats Inline for Match"""
    model = PlayerMatchStats
    extra = 1
    fields = ['player', 'team', 'goals', 'assists', 'played']
    autocomplete_fields = ['player', 'team']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'week', 'date', 'team1_score', 'team2_score', 'is_finished', 'winner']
    list_filter = ['week', 'is_finished', 'date', 'team1', 'team2']
    search_fields = ['team1__name', 'team2__name']
    date_hierarchy = 'date'
    inlines = [PlayerMatchStatsInline]
    # Turkish Admin Panel
    fieldsets = (
        ('Maç Bilgileri', {
            'fields': ('week', 'date', 'team1', 'team2' , 'referee' , 'is_score_editable')
        }),
        ('Skor', {
            'fields': ('team1_score', 'team2_score', 'is_finished')
        }),
    )
    
    def winner(self, obj):
       
        winner = obj.winner
        if winner:
            return f"{winner.name}"
        return "Beraberlik" if obj.is_finished else "Devam Ediyor"
    winner.short_description = 'Kazanan'


@admin.register(PlayerMatchStats)
class PlayerMatchStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'team', 'goals', 'assists', 'played']
    list_filter = ['played', 'team', 'match__date']
    search_fields = ['player__name', 'match__team1__name', 'match__team2__name']
    autocomplete_fields = ['player', 'match', 'team']
    
    fieldsets = (
        ('Maç ve Oyuncu', {
            'fields': ('match', 'player', 'team')
        }),
        ('İstatistikler', {
            'fields': ('goals', 'assists', 'played')
        }),
    )
