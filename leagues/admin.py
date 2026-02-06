from django.contrib import admin
from .models import League, Week, Standing

class WeekInline(admin.TabularInline):
    model = Week
    extra = 1

class StandingInline(admin.TabularInline):
    model = Standing
    extra = 0
    readonly_fields = ('played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'points')
    can_delete = False

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'season', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    inlines = [WeekInline, StandingInline]

@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'start_date', 'end_date', 'is_played']
    list_filter = ['league', 'is_played']
    search_fields = ['name', 'league__name']

@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ['team', 'league', 'points', 'played', 'wins', 'draws', 'losses', 'goal_difference']
    list_filter = ['league']
    search_fields = ['team__name', 'league__name']
    readonly_fields = ('goal_difference',)
