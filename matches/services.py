from django.db.models import Avg, Sum
from players.models import Player
from .models import PlayerMatchRating
from django.db import models 

class RatingService:
    @staticmethod
    def update_player_overall(player_id, new_rating=None):
        """
        Updates player stats using running totals for performance.
        """
        try:
            player = Player.objects.get(id=player_id)
            
            if new_rating:
                # INCREMENTAL UPDATE (O(1))
                #print(f"Before Update -  Count: {player.rating_count}, TotalPace: {player.total_rating_pace}")
                
                player.rating_count += 1
                
                # Update Totals
                player.total_rating_pace += new_rating.rating_pace
                player.total_rating_shooting += new_rating.rating_shooting
                player.total_rating_passing += new_rating.rating_passing
                player.total_rating_dribbling += new_rating.rating_dribbling
                player.total_rating_defense += new_rating.rating_defense
                player.total_rating_physical += new_rating.rating_physical
                
                # GK Totals
                player.total_rating_diving += new_rating.rating_diving
                player.total_rating_handling += new_rating.rating_handling
                player.total_rating_kicking += new_rating.rating_kicking
                player.total_rating_reflexes += new_rating.rating_reflexes
                player.total_rating_speed += new_rating.rating_speed
                player.total_rating_positioning += new_rating.rating_positioning
                
                #print(f"DEBUG: Adding rating: Pace={new_rating.rating_pace}")
                #print(f"DEBUG: After Update - Count: {player.rating_count}, TotalPace: {player.total_rating_pace}")
                
                
            else:

                # FULL RECALCULATION (O(N)) - Only for migration/maintenance or make correction
                # This clear totals and re-sum everything
                ratings = PlayerMatchRating.objects.filter(rated_player=player)
                player.rating_count = ratings.count()
                if player.rating_count == 0:
                    return

                aggregates = ratings.aggregate(
                    sum_pace=models.Sum('rating_pace'),
                    sum_shooting=models.Sum('rating_shooting'),
                    sum_passing=models.Sum('rating_passing'),
                    sum_dribbling=models.Sum('rating_dribbling'),
                    sum_defense=models.Sum('rating_defense'),
                    sum_physical=models.Sum('rating_physical'),
                    # GK Stats
                    sum_diving=models.Sum('rating_diving'),
                    sum_handling=models.Sum('rating_handling'),
                    sum_kicking=models.Sum('rating_kicking'),
                    sum_reflexes=models.Sum('rating_reflexes'),
                    sum_speed=models.Sum('rating_speed'),
                    sum_positioning=models.Sum('rating_positioning'),
                )
                player.total_rating_pace = aggregates['sum_pace'] or 0
                player.total_rating_shooting = aggregates['sum_shooting'] or 0
                player.total_rating_passing = aggregates['sum_passing'] or 0
                player.total_rating_dribbling = aggregates['sum_dribbling'] or 0
                player.total_rating_defense = aggregates['sum_defense'] or 0
                player.total_rating_physical = aggregates['sum_physical'] or 0
                # GK Totals
                player.total_rating_diving = aggregates['sum_diving'] or 0
                player.total_rating_handling = aggregates['sum_handling'] or 0
                player.total_rating_kicking = aggregates['sum_kicking'] or 0
                player.total_rating_reflexes = aggregates['sum_reflexes'] or 0
                player.total_rating_speed = aggregates['sum_speed'] or 0
                player.total_rating_positioning = aggregates['sum_positioning'] or 0

            # Helper to normalize
            def normalize(val):
                if val is None: return 75
                # Range 1-10 to 75-99
                # Formula: 75 + (val * 2.5)
                try:
                    score = 75 + (float(val) * 2.5)
                    return int(min(99, score))
                except (ValueError, TypeError):
                    return 75

            # Calculate Averages for Display
            count = player.rating_count if player.rating_count > 0 else 1
            
            player.pace = normalize(player.total_rating_pace / count)
            player.shooting = normalize(player.total_rating_shooting / count)
            player.passing = normalize(player.total_rating_passing / count)
            player.dribbling = normalize(player.total_rating_dribbling / count)
            player.defense = normalize(player.total_rating_defense / count)
            player.physical = normalize(player.total_rating_physical / count)
            
            # GK Stats
            player.diving = normalize(player.total_rating_diving / count)
            player.handling = normalize(player.total_rating_handling / count)
            player.kicking = normalize(player.total_rating_kicking / count)
            player.reflexes = normalize(player.total_rating_reflexes / count)
            player.speed = normalize(player.total_rating_speed / count)
            player.positioning = normalize(player.total_rating_positioning / count)
            
            
            # Recalculate Overall
            player.overall = player.calculate_overall()
            player.save()
            
            print(f"Updated stats for {player.name}: Overall {player.overall}")
            
        except Player.DoesNotExist:
            print(f"Player {player_id} not found during rating update.")
        except Exception as e:
            print(f"Error updating player ratings: {e}")
