from itertools import combinations
from statistics import mean

# Sorts players in a list based on their role. Focuses
def role_sort(players, roles_needed):
    tanks = []
    damage = []
    supports = []

    # Assign players by their preferred roles
    for player in players:
        if player.preferred_role == "tank":
            tanks.append(player)
        elif player.preferred_role == "damage":
            damage.append(player)
        elif player.preferred_role == "support":
            supports.append(player)

    # Fill missing roles with secondary roles if necessary
    if len(tanks) < roles_needed["tank"]:
        for player in players:
            if player.secondary_role == "tank" and player not in tanks:
                tanks.append(player)
            if len(tanks) == roles_needed["tank"]:
                break

    if len(damage) < roles_needed["damage"]:
        for player in players:
            if player.secondary_role == "damage" and player not in damage:
                damage.append(player)
            if len(damage) == roles_needed["damage"]:
                break

    if len(supports) < roles_needed["support"]:
        for player in players:
            if player.secondary_role == "support" and player not in supports:
                supports.append(player)
            if len(supports) == roles_needed["support"]:
                break

    # Sort players by rank
    tanks = sorted(tanks, key=lambda p: p.sr, reverse=True)
    damage = sorted(damage, key=lambda p: p.sr, reverse=True)
    supports = sorted(supports, key=lambda p: p.sr, reverse=True)

    # Assign players to teams, checking if there are enough players
    team1 = {
        "tank": [tanks[0]] if len(tanks) > 0 else [],
        "damage": [damage[0], damage[3]] if len(damage) > 2 else damage[:2],
        "support": [supports[0], supports[3]] if len(supports) > 2 else supports[:2]
    }

    team2 = {
        "tank": [tanks[1]] if len(tanks) > 1 else [],
        "damage": [damage[1], damage[2]] if len(damage) > 3 else damage[1:],
        "support": [supports[1], supports[2]] if len(supports) > 3 else supports[1:]
    }

    return team1, team2

# Sorts teams and tries to find the closest teams to play against each other. Exhaustive search
def sort_teams(players):
    # Split players into roles
    tanks = [p for p in players if p.preferred_role == "Tank"]
    dps = [p for p in players if p.preferred_role == "Damage"]
    supports = [p for p in players if p.preferred_role == "Support"]

    # Function to calculate average rank of a team
    def calculate_team_rank(team):
        return mean([player.sr for player in team])

    # Find the best balanced teams
    min_difference = float('inf')
    
    # Iterate over all possible combinations
    for team1 in combinations(tanks + dps + supports, 5):
        team2 = [p for p in players if p not in team1]
        
        best_team_1 = None
        best_team_2 = None
        
        # Check role requirements
        if sum(1 for p in team1 if p.preferred_role == "Tank") == 1 and sum(1 for p in team1 if p.preferred_role == "Damage") == 2 and sum(1 for p in team1 if p.preferred_role == "Support") == 2 and \
        sum(1 for p in team2 if p.preferred_role == "Tank") == 1 and sum(1 for p in team2 if p.preferred_role == "Damage") == 2 and sum(1 for p in team2 if p.preferred_role == "Support") == 2:
            
            # Calculate rank differences
            team1_rank = calculate_team_rank(team1)
            team2_rank = calculate_team_rank(team2)
            difference = abs(team1_rank - team2_rank)
            
            # Track best teams
            if difference < min_difference:
                min_difference = difference
                best_team_1 = team1
                best_team_2 = team2
    
    return best_team_1, best_team_2