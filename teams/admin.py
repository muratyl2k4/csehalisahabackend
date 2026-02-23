from django.contrib import admin
from .models import Team, TransferRequest
from leagues.models import Standing

class StandingInline(admin.TabularInline):
    model = Standing
    extra = 0
    can_delete = False
    fields = ('league', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'points')
    readonly_fields = ('league',) # Prevent changing league from here, only stats

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'short_name']
    readonly_fields = ['created_at']
    inlines = [StandingInline]
    
    fieldsets = (
        ('Takım Bilgileri', {
            'fields': ('captain','name', 'short_name', 'logo')
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
