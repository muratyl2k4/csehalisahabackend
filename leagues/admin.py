from django.contrib import admin
from .models import League, Week, Standing, Tournament, TournamentMatch

class WeekInline(admin.TabularInline):
    model = Week
    extra = 1

class StandingInline(admin.TabularInline):
    model = Standing
    extra = 0
    # Allow editing (removed readonly_fields)
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
    list_display = ['team', 'league', 'points', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_difference']
    list_editable = ['points', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against']
    list_filter = ['league']
    search_fields = ['team__name', 'league__name']
    readonly_fields = ('goal_difference',)

class TournamentMatchInline(admin.StackedInline): # Stacked better for many fields
    model = TournamentMatch
    extra = 1
    fk_name = 'tournament'
    fields = ('round_name', 'round_index', 'date', 'team1', 'team2', 'next_match', 'is_finished')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'created_at']
    inlines = [TournamentMatchInline]

@admin.register(TournamentMatch)
class TournamentMatchAdmin(admin.ModelAdmin):
    list_display = ['round_name', 'team1', 'team2', 'date', 'is_finished', 'next_match', 'tournament']
    list_filter = ['tournament', 'round_name', 'is_finished']
    search_fields = ['team1__name', 'team2__name', 'round_name']
    
    fieldsets = (
        ('Turnuva Bilgisi', {
            'fields': ('tournament', 'round_name', 'round_index', 'next_match', 'position')
        }),
        ('Maç Verileri', {
            'fields': ('date', 'team1', 'team2', 'referee', 'is_score_editable')
        }),
        ('Skor', {
            'fields': ('team1_score', 'team2_score', 'is_finished')
        }),
    )
