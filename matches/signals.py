from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# Import Rating Logic
from .models import PlayerMatchStats, Match, PlayerMatchRating
from .services import RatingService

@receiver(post_save, sender=PlayerMatchRating)
def update_player_rating_on_save(sender, instance, created, **kwargs):
    """
    Update player stats automatically when a rating is created or updated.
    This covers Admin Panel, API, and Shell usage.
    """
    if created:
        # Incremental update
        RatingService.update_player_overall(instance.rated_player.id, new_rating=instance)
    else:
        # If updated, we might need a full recalc because we don't know the delta easily
        # For now, let's just do full recalc to be safe.
        RatingService.update_player_overall(instance.rated_player.id, new_rating=None)

@receiver(pre_save, sender=PlayerMatchStats)
def update_match_score_on_goal_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_stat = PlayerMatchStats.objects.get(pk=instance.pk)
            goal_diff = instance.goals - old_stat.goals
            
            if goal_diff != 0:
                match = instance.match
                if instance.team == match.team1:
                    match.team1_score += goal_diff
                elif instance.team == match.team2:
                    match.team2_score += goal_diff
                
                # Prevent negative scores just in case
                if match.team1_score < 0: match.team1_score = 0
                if match.team2_score < 0: match.team2_score = 0
                
                match.save(update_fields=['team1_score', 'team2_score'])
        except PlayerMatchStats.DoesNotExist:
            pass # New instance, handled in post_save if needed, or initialized with 0

@receiver(post_save, sender=PlayerMatchStats)
def update_match_score_on_new_stat(sender, instance, created, **kwargs):
    if created and instance.goals > 0:
        match = instance.match
        if instance.team == match.team1:
            match.team1_score += instance.goals
        elif instance.team == match.team2:
            match.team2_score += instance.goals
        match.save(update_fields=['team1_score', 'team2_score'])

@receiver(post_save, sender=Match)
@receiver(post_save, sender='leagues.TournamentMatch')
def create_initial_player_stats(sender, instance, created, **kwargs):
    """
    When a match is created, automatically create PlayerMatchStats for all players
    in both teams.
    """
    if created:
        # Team 1 Players
        if instance.team1:
            for player in instance.team1.players.all():
                PlayerMatchStats.objects.get_or_create(
                    match=instance,
                    player=player,
                    defaults={'team': instance.team1}
                )
        
        # Team 2 Players
        if instance.team2:
            for player in instance.team2.players.all():
                PlayerMatchStats.objects.get_or_create(
                    match=instance,
                    player=player,
                    defaults={'team': instance.team2}
                )




@receiver(pre_save, sender=Match)
@receiver(pre_save, sender='leagues.TournamentMatch')
def capture_old_match_state(sender, instance, **kwargs):
    """
    Capture the state of the match before saving to handle standings updates.
    """
    if instance.pk:
        try:
            instance._old_match = Match.objects.get(pk=instance.pk)
        except Match.DoesNotExist:
            instance._old_match = None
    else:
        instance._old_match = None

@receiver(post_save, sender=Match)
@receiver(post_save, sender='leagues.TournamentMatch')
def update_standings_on_match_finish(sender, instance, created, **kwargs):
    """
    Update league standings when a match is finished or modified.
    Also handles tournament progression for TournamentMatch instances.
    """
    old_match = getattr(instance, '_old_match', None)
    
    # helper functions defined inside to keep scope clean
    def _update_standings(match):
        from leagues.models import Standing
        if not match.week or not match.week.league: return
        league = match.week.league
        
        # Team 1
        s1, _ = Standing.objects.get_or_create(league=league, team=match.team1)
        s1.played += 1
        s1.goals_for += match.team1_score
        s1.goals_against += match.team2_score
        if match.team1_score > match.team2_score:
            s1.wins += 1
            s1.points += 3
        elif match.team1_score == match.team2_score:
            s1.draws += 1
            s1.points += 1
        else:
            s1.losses += 1
        s1.save()
        
        # Team 2
        s2, _ = Standing.objects.get_or_create(league=league, team=match.team2)
        s2.played += 1
        s2.goals_for += match.team2_score
        s2.goals_against += match.team1_score
        if match.team2_score > match.team1_score:
            s2.wins += 1
            s2.points += 3
        elif match.team2_score == match.team1_score:
            s2.draws += 1
            s2.points += 1
        else:
            s2.losses += 1
        s2.save()

    def _revert_standings(match):
        from leagues.models import Standing
        if not match.week or not match.week.league: return
        league = match.week.league
        
        def revert_team(team, gf, ga):
            try:
                s = Standing.objects.get(league=league, team=team)
                s.played -= 1
                s.goals_for -= gf
                s.goals_against -= ga
                if gf > ga:
                    s.wins -= 1
                    s.points -= 3
                elif gf == ga:
                    s.draws -= 1
                    s.points -= 1
                else:
                    s.losses -= 1
                s.save()
            except Standing.DoesNotExist:
                pass

        revert_team(match.team1, match.team1_score, match.team2_score)
        revert_team(match.team2, match.team2_score, match.team1_score)

    # --- 1. Tournament Progression (Subclass only) ---
    if instance.is_finished:
        if created or (old_match and not old_match.is_finished):
            try:
                from leagues.models import TournamentMatch
                # Direct query to ensure we get the subclass instance
                node = TournamentMatch.objects.filter(pk=instance.pk).first()
                
                if node and node.next_match:
                    winner = instance.winner
                    if winner:
                        next_node = node.next_match
                        updated = False
                        
                        # Use actual Team objects for comparison
                        if not next_node.team1:
                            next_node.team1 = winner
                            updated = True
                        elif not next_node.team2 and next_node.team1_id != winner.id:
                            next_node.team2 = winner
                            updated = True
                        
                        if updated:
                            next_node.save()
            except Exception:
                pass

    # --- 2. League Standings (League matches only) ---
    if instance.match_type == 'LEAGUE':
        if instance.is_finished:
            if created or (old_match and not old_match.is_finished):
                _update_standings(instance)
            elif old_match and (old_match.team1_score != instance.team1_score or old_match.team2_score != instance.team2_score or old_match.team1 != instance.team1 or old_match.team2 != instance.team2):
                _revert_standings(old_match)
                _update_standings(instance)
        elif old_match and old_match.is_finished:
            # Match was finished but now is NOT finished
            _revert_standings(old_match)
