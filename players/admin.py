from django.contrib import admin
from .models import Player


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Oyuncu Profili'

class UserAdmin(BaseUserAdmin):
    inlines = (PlayerInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'age', 'current_team', 'position', 'overall']
    list_filter = ['current_team', 'position', 'age']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_goals', 'overall', 'total_assists', 'matches_played']
    #Turkish Admin Panel
    fieldsets = (
        ('Hesap Bilgisi', {
            'fields': ('user',)
        }),
        ('Kişisel Bilgiler', {
            'fields': ('name', 'age', 'photo', 'current_team', 'position')
        }),
        ('Oyuncu İstatistikleri', {
            'fields': ('overall', 'pace', 'shooting', 'passing', 'dribbling', 'defense', 'physical',
                       )
        }),
        ('Kaleci İstatistikleri', {
            'fields': ('diving', 'handling', 'kicking', 'reflexes', 'speed', 'positioning',
                       )
        }),
        ('Maç İstatistikleri', {
            'fields': ('total_goals', 'total_assists', 'matches_played'),
            'description': 'Bu değerler maç sonuçlarından otomatik hesaplanır.'
        }),
        ('Diğer', {
            'fields': ('created_at', 'updated_at')
        }),
    )
