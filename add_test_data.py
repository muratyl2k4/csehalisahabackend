"""
Test verileri ekleme scripti - Büyük Dataset
Django shell ile çalıştırılır: python manage.py shell < add_test_data.py
"""

from teams.models import Team
from players.models import Player
from matches.models import Match, PlayerMatchStats
from datetime import datetime, timedelta
import random

print("Büyük test veri seti ekleniyor...")

# Önce mevcut verileri temizle
PlayerMatchStats.objects.all().delete()
Match.objects.all().delete()
Player.objects.all().delete()
Team.objects.all().delete()

# 10 Takım - Gençler arası takım isimleri
team_names = [
    "Yok Ediciler",
    "Trabzonlular",
    "Şampiyonlar",
    "Karadeniz Fırtınası",
    "Sokak Savaşçıları",
    "Genç Yıldızlar",
    "Aslan Pençeleri",
    "Mavi Şimşekler",
    "Kızıl Fırtına",
    "Altın Nesil"
]

teams = []
for team_name in team_names:
    team = Team.objects.create(name=team_name, wins=0, losses=0)
    teams.append(team)
    print(f"✓ Takım oluşturuldu: {team.name}")

# Türk isimleri havuzu
first_names = [
    "Ahmet", "Mehmet", "Ali", "Mustafa", "Hasan", "Hüseyin", "İbrahim", "Yusuf", "Ömer", "Murat",
    "Emre", "Cem", "Burak", "Kaan", "Eren", "Arda", "Oğuz", "Berk", "Can", "Deniz",
    "Kerem", "Barış", "Onur", "Selim", "Furkan", "Serkan", "Volkan", "Uğur", "Tarık", "Okan",
    "Cenk", "Tolga", "Umut", "Koray", "Tunç", "Alper", "Görkem", "Tuncay", "Rıza", "Sefa",
    "Yasin", "Bilal", "Halil", "Cemal", "Ramazan", "Recep", "Salih", "Kadir", "Emir", "Samet",
    "Sinan", "Taner", "Vedat", "Zafer", "Orhan", "Hamza", "İsmail", "Veli", "Yılmaz", "Zeki",
    "Erol", "Erkan", "Fatih", "Gökhan", "Hakan", "İlhan", "Kemal", "Levent", "Nihat", "Özgür"
]

last_names = [
    "Yılmaz", "Demir", "Şahin", "Çelik", "Koç", "Kaya", "Aydın", "Özdemir", "Arslan", "Doğan",
    "Kılıç", "Aslan", "Çetin", "Kara", "Aksoy", "Türk", "Kurt", "Özkan", "Şimşek", "Erdoğan",
    "Öztürk", "Aydin", "Yıldız", "Polat", "Güneş", "Korkmaz", "Tekin", "Aktaş", "Bulut", "Keskin",
    "Biçer", "Bilici", "Zengin", "Özer", "Topal", "Akın", "Durmaz", "Yavuz", "Güler", "Karaca",
    "Toprak", "Ateş", "Sönmez", "Deniz", "Taş", "Özgül", "Uysal", "Şen", "Ada", "Özkaya",
    "Turan", "Eren", "Soylu", "Tan", "Bozkurt", "Çakır", "Yalçın", "Aksu", "Demirci", "Can",
    "Vural", "Bayram", "Işık", "Gül", "Acar", "Uzun", "Sarı", "Koçak", "Akman", "Çiftçi"
]

positions = ["ST", "LW", "RW", "CAM", "CM", "CDM", "CB"]

# 70 Oyuncu (her takımda 7 oyuncu)
all_players = []
player_count = 0

for team in teams:
    team_players = []
    for i in range(7):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Pozisyona göre stats
        position = positions[i]
        
        if position == "ST":
            player = Player.objects.create(
                name=full_name,
                age=random.randint(18, 32),
                photo="2.png",
                current_team=team,
                position=position,
                overall=random.randint(75, 92),
                pace=random.randint(70, 90),
                shooting=random.randint(80, 95),
                passing=random.randint(60, 78),
                dribbling=random.randint(70, 88),
                defense=random.randint(30, 50),
                physical=random.randint(70, 88)
            )
        elif position in ["LW", "RW"]:
            player = Player.objects.create(
                name=full_name,
                age=random.randint(18, 30),
                photo="2.png",
                current_team=team,
                position=position,
                overall=random.randint(73, 89),
                pace=random.randint(80, 95),
                shooting=random.randint(70, 88),
                passing=random.randint(68, 82),
                dribbling=random.randint(80, 93),
                defense=random.randint(30, 48),
                physical=random.randint(60, 75)
            )
        elif position == "CAM":
            player = Player.objects.create(
                name=full_name,
                age=random.randint(20, 32),
                photo="2.png",
                current_team=team,
                position=position,
                overall=random.randint(75, 90),
                pace=random.randint(68, 82),
                shooting=random.randint(75, 88),
                passing=random.randint(80, 92),
                dribbling=random.randint(78, 90),
                defense=random.randint(40, 55),
                physical=random.randint(60, 75)
            )
        elif position == "CM":
            player = Player.objects.create(
                name=full_name,
                age=random.randint(20, 32),
                photo="2.png",
                current_team=team,
                position=position,
                overall=random.randint(73, 87),
                pace=random.randint(65, 80),
                shooting=random.randint(65, 80),
                passing=random.randint(75, 88),
                dribbling=random.randint(70, 84),
                defense=random.randint(65, 78),
                physical=random.randint(70, 82)
            )
        elif position == "CDM":
            player = Player.objects.create(
                name=full_name,
                age=random.randint(22, 34),
                photo="2.png",
                current_team=team,
                position=position,
                overall=random.randint(75, 88),
                pace=random.randint(60, 75),
                shooting=random.randint(55, 72),
                passing=random.randint(72, 85),
                dribbling=random.randint(65, 78),
                defense=random.randint(78, 90),
                physical=random.randint(75, 88)
            )
        else:  # CB
            player = Player.objects.create(
                name=full_name,
                age=random.randint(22, 35),
                photo="2.png",
                current_team=team,
                position=position,
                overall=random.randint(74, 89),
                pace=random.randint(55, 72),
                shooting=random.randint(35, 55),
                passing=random.randint(60, 75),
                dribbling=random.randint(50, 68),
                defense=random.randint(80, 92),
                physical=random.randint(78, 90)
            )
        
        team_players.append(player)
        all_players.append(player)
        player_count += 1
    
    print(f"✓ {team.name}: {len(team_players)} oyuncu oluşturuldu")

print(f"\nToplam {player_count} oyuncu oluşturuldu")

# 50 Maç - Her maçta minimum 10 gol
print("\nMaçlar oluşturuluyor...")
matches_created = 0

for i in range(50):
    # Rastgele iki takım seç
    team1, team2 = random.sample(teams, 2)
    
    # Her maçta minimum 10 gol - Daha yüksek skorlar
    min_total_goals = 10
    max_total_goals = 15
    total_goals = random.randint(min_total_goals, max_total_goals)
    
    # Golü iki takıma dağıt (biraz randomize)
    team1_score = random.randint(3, total_goals - 3)
    team2_score = total_goals - team1_score
    
    # Tarih (son 60 günden rastgele)
    match_date = datetime.now() - timedelta(days=random.randint(1, 60))
    
    match = Match.objects.create(
        date=match_date,
        team1=team1,
        team2=team2,
        team1_score=team1_score,
        team2_score=team2_score,
        is_finished=True
    )
    
    # Takım 1 oyuncuları için stats
    team1_players = list(Player.objects.filter(current_team=team1))
    goals_left = team1_score
    assists_available = team1_score
    
    random.shuffle(team1_players)
    
    # İlk oyuncuya kesin gol (forvet varsa)
    for player in team1_players:
        if goals_left == 0:
            # Gol bitti, sadece asist verebilir
            player_goals = 0
            player_assists = random.randint(0, min(assists_available, 2))  if assists_available > 0 else 0
            assists_available -= player_assists
        else:
            # Forvet ve kanatlara daha fazla gol şansı
            if player.position in ["ST", "LW", "RW"]:
                max_goals = min(goals_left, random.randint(1, 4))  # 1-4 gol
            elif player.position == "CAM":
                max_goals = min(goals_left, random.randint(0, 3))  # 0-3 gol
            else:
                max_goals = min(goals_left, random.randint(0, 2))  # 0-2 gol
            
            player_goals = random.randint(0, max_goals) if max_goals > 0 else 0
            
            # Son oyuncuya kalan golları ver
            if player == team1_players[-1] and goals_left > 0:
                player_goals = goals_left
            
            goals_left -= player_goals
            
            player_assists = random.randint(0, min(assists_available, 2)) if assists_available > 0 else 0
            assists_available -= player_assists
        
        PlayerMatchStats.objects.create(
            match=match,
            player=player,
            team=team1,
            goals=player_goals,
            assists=player_assists,
            played=True
        )
    
    # Takım 2 oyuncuları için stats
    team2_players = list(Player.objects.filter(current_team=team2))
    goals_left = team2_score
    assists_available = team2_score
    
    random.shuffle(team2_players)
    
    for player in team2_players:
        if goals_left == 0:
            player_goals = 0
            player_assists = random.randint(0, min(assists_available, 2)) if assists_available > 0 else 0
            assists_available -= player_assists
        else:
            if player.position in ["ST", "LW", "RW"]:
                max_goals = min(goals_left, random.randint(1, 4))
            elif player.position == "CAM":
                max_goals = min(goals_left, random.randint(0, 3))
            else:
                max_goals = min(goals_left, random.randint(0, 2))
            
            player_goals = random.randint(0, max_goals) if max_goals > 0 else 0
            
            # Son oyuncuya kalan golları ver
            if player == team2_players[-1] and goals_left > 0:
                player_goals = goals_left
            
            goals_left -= player_goals
            
            player_assists = random.randint(0, min(assists_available, 2)) if assists_available > 0 else 0
            assists_available -= player_assists
        
        PlayerMatchStats.objects.create(
            match=match,
            player=player,
            team=team2,
            goals=player_goals,
            assists=player_assists,
            played=True
        )
    
    matches_created += 1
    if matches_created % 10 == 0:
        print(f"✓ {matches_created} maç oluşturuldu...")

print(f"\nToplam {matches_created} maç oluşturuldu!")


# İstatistikler
print("\n" + "="*60)
print("TEST VERİLERİ BAŞARIYLA EKLENDİ!")
print("="*60)
print(f"\n📊 Özet:")
print(f"   🏆 {Team.objects.count()} takım")
print(f"   ⭐ {Player.objects.count()} oyuncu")
print(f"   ⚽ {Match.objects.count()} maç")
print(f"   📈 {PlayerMatchStats.objects.count()} oyuncu maç istatistiği")

# Gol kralları
from django.db.models import Sum
print(f"\n🥇 GOL KRALLARI TOP 5:")
goal_leaders = Player.objects.annotate(
    total_goals=Sum('match_stats__goals')
).order_by('-total_goals')[:5]

for i, player in enumerate(goal_leaders, 1):
    total = player.total_goals or 0
    print(f"   {i}. ⚽ {player.name} ({player.current_team.name}): {total} gol")

# Asist kralları
print(f"\n🎯 ASİST KRALLARI TOP 5:")
assist_leaders = Player.objects.annotate(
    total_assists=Sum('match_stats__assists')
).order_by('-total_assists')[:5]

for i, player in enumerate(assist_leaders, 1):
    total = player.total_assists or 0
    print(f"   {i}. 🎯 {player.name} ({player.current_team.name}): {total} asist")

# Takım sıralaması
print(f"\n🏆 TAKIM SIRALAMALARI:")
ranked_teams = Team.objects.all().order_by('-wins', 'losses')
for i, team in enumerate(ranked_teams, 1):
    print(f"   {i}. {team.name}: {team.wins}G {team.draws}B {team.losses}M ({team.win_rate}% kazanma)")

print("\n✅ Tüm veriler hazır! Frontend'i test edebilirsiniz.")

