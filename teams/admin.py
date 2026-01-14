from django.contrib import admin
from .models import Team, TransferRequest


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'wins', 'losses', 'total_matches', 'win_rate', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'short_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Takım Bilgileri', {
            'fields': ('captain','name', 'short_name', 'logo')
        }),
        ('İstatistikler', {
            'fields': ('wins', 'losses')
        }),
        ('Diğer', {
            'fields': ('created_at',)
        }),
    )

@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ['player', 'team', 'status', 'created_at']
    list_filter = ['status', 'team']
    search_fields = ['player__user__username', 'player__name', 'team__name']
