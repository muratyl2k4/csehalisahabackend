from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'current_team', 'position', 'overall', 'total_goals', 'total_assists', 'matches_played']
    list_filter = ['current_team', 'position', 'age']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'total_goals', 'total_assists', 'matches_played']
    
    fieldsets = (
        ('Kişisel Bilgiler', {
            'fields': ('name', 'age', 'photo', 'current_team', 'position')
        }),
        ('FIFA İstatistikleri', {
            'fields': ('overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical')
        }),
        ('Maç İstatistikleri', {
            'fields': ('total_goals', 'total_assists', 'matches_played'),
            'description': 'Bu değerler maç sonuçlarından otomatik hesaplanır.'
        }),
        ('Diğer', {
            'fields': ('created_at', 'updated_at')
        }),
    )
