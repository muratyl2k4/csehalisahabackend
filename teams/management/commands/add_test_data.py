"""
Django management command - Test verileri ekleme
Kullanim: python manage.py add_test_data
"""

from django.core.management.base import BaseCommand
from teams.models import Team
from players.models import Player
from matches.models import Match, PlayerMatchStats
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = '10 takim, 70 oyuncu (7/takim), 50 mac test verisi ekler'

    def handle(self, *args, **options):
        self.stdout.write("Test veri seti ekleniyor...")
        
        # Mevcut verileri temizle
        PlayerMatchStats.objects.all().delete()
        Match.objects.all().delete()
        Player.objects.all().delete()
        Team.objects.all().delete()
        
        # 10 Takim
        team_names = [
            "Yok Ediciler",
            "Trabzonlular",
            "Sampiyonlar",
            "Karadeniz Firtinasi",
            "Sokak Savascilari",
            "Genc Yildizlar",
            "Aslan Penceleri",
            "Mavi Simsekler",
            "Kizil Firtina",
            "Altin Nesil"
        ]
        
        teams = []
        for team_name in team_names:
            team = Team.objects.create(name=team_name, wins=0, losses=0)
            teams.append(team)
            self.stdout.write(f"+ Takim olusturuldu: {team.name}")
        
        # Turk isimleri havuzu
        first_names = [
            "Ahmet", "Mehmet", "Ali", "Mustafa", "Hasan", "Huseyin", "Ibrahim", "Yusuf", "Omer", "Murat",
            "Emre", "Cem", "Burak", "Kaan", "Eren", "Arda", "Oguz", "Berk", "Can", "Deniz",
            "Kerem", "Baris", "Onur", "Selim", "Furkan", "Serkan", "Volkan", "Ugur", "Tarik", "Okan",
            "Cenk", "Tolga", "Umut", "Koray", "Tunc", "Alper", "Gorkem", "Tuncay", "Riza", "Sefa",
            "Yasin", "Bilal", "Halil", "Cemal", "Ramazan", "Recep", "Salih", "Kadir", "Emir", "Samet",
            "Sinan", "Taner", "Vedat", "Zafer", "Orhan", "Hamza", "Ismail", "Veli", "Yilmaz", "Zeki",
            "Erol", "Erkan", "Fatih", "Gokhan", "Hakan", "Ilhan", "Kemal", "Levent", "Nihat", "Ozgur"
        ]
        
        last_names = [
            "Yilmaz", "Demir", "Sahin", "Celik", "Koc", "Kaya", "Aydin", "Ozdemir", "Arslan", "Dogan",
            "Kilic", "Aslan", "Cetin", "Kara", "Aksoy", "Turk", "Kurt", "Ozkan", "Simsek", "Erdogan",
            "Ozturk", "Aydin", "Yildiz", "Polat", "Gunes", "Korkmaz", "Tekin", "Aktas", "Bulut", "Keskin",
            "Bicer", "Bilici", "Zengin", "Ozer", "Topal", "Akin", "Durmaz", "Yavuz", "Guler", "Karaca",
            "Toprak", "Ates", "Sonmez", "Deniz", "Tas", "Ozgul", "Uysal", "Sen", "Ada", "Ozkaya",
            "Turan", "Eren", "Soylu", "Tan", "Bozkurt", "Cakir", "Yalcin", "Aksu", "Demirci", "Can",
            "Vural", "Bayram", "Isik", "Gul", "Acar", "Uzun", "Sari", "Kocak", "Akman", "Ciftci"
        ]
        
        positions = ["ST", "LW", "RW", "CAM", "CM", "CDM", "CB"]
        
        # 70 Oyuncu (her takimda 7 oyuncu)
        all_players = []
        player_count = 0
        
        for team in teams:
            team_players = []
            for i in range(7):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                full_name = f"{first_name} {last_name}"
                
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
            
            self.stdout.write(f"+ {team.name}: {len(team_players)} oyuncu olusturuldu")
        
        self.stdout.write(f"\nToplam {player_count} oyuncu olusturuldu")
        
        # 50 Mac - Her macta minimum 10 gol
        self.stdout.write("\nMaclar olusturuluyor...")
        matches_created = 0
        
        for i in range(50):
            # Rastgele iki takim sec
            team1, team2 = random.sample(teams, 2)
            
            # Her macta minimum 10 gol  
            min_total_goals = 10
            max_total_goals = 15
            total_goals = random.randint(min_total_goals, max_total_goals)
            
            # Golu iki takima dagit
            team1_score = random.randint(3, total_goals - 3)
            team2_score = total_goals - team1_score
            
            # Tarih
            match_date = datetime.now() - timedelta(days=random.randint(1, 60))
            
            match = Match.objects.create(
                date=match_date,
                team1=team1,
                team2=team2,
                team1_score=team1_score,
                team2_score=team2_score,
                is_finished=True
            )
            
            # Takim 1 oyunculari icin stats
            team1_players = list(Player.objects.filter(current_team=team1))
            goals_left = team1_score
            assists_available = team1_score
            
            random.shuffle(team1_players)
            
            for player in team1_players:
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
            
            # Takim 2 oyunculari icin stats
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
                self.stdout.write(f"+ {matches_created} mac olusturuldu...")
        
        self.stdout.write(f"\nToplam {matches_created} mac olusturuldu!")
        
        # Istatistikler
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("TEST VERILERI BASARIYLA EKLENDI!"))
        self.stdout.write("="*60)
        self.stdout.write(f"\nOzet:")
        self.stdout.write(f"   {Team.objects.count()} takim")
        self.stdout.write(f"   {Player.objects.count()} oyuncu")
        self.stdout.write(f"   {Match.objects.count()} mac")
        self.stdout.write(f"   {PlayerMatchStats.objects.count()} oyuncu mac istatistigi")
        
        self.stdout.write(self.style.SUCCESS("\nTum veriler hazir! Frontend'i test edebilirsiniz."))
