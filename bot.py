import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='??', intents=intents)

# Player class to store player info
class Player:
    def __init__(self, battle_tag, rank, preferred_role, secondary_role):
        self.battle_tag = battle_tag
        self.rank = int(rank)  # Assuming rank is an integer
        self.preferred_role = preferred_role
        self.secondary_role = secondary_role

# Global player pool to store current PUG players
player_pool = []

# Dictionary to hold players based on role preferences
roles_needed = {
    "tank": 2,
    "damage": 4,
    "support": 4
}

# Command to join the PUG
@bot.command()
async def join(ctx, battle_tag: str, rank: int, preferred_role: str, secondary_role: str):
    if len(player_pool) >= 10:
        await ctx.send("Player pool is already full. Wait for the next game!")
        return
    
    # Validate the input for roles
    if preferred_role not in ["tank", "damage", "support"] or secondary_role not in ["tank", "damage", "support"]:
        await ctx.send("Invalid role. Use one of the following: tank, damage, support.")
        return
    
    # Add player to the player pool
    player = Player(battle_tag, rank, preferred_role, secondary_role)
    player_pool.append(player)
    await ctx.send(f"{battle_tag} has joined the game! Current players: {len(player_pool)}/10")

    # Once 10 players are in the pool, sort and create teams
    if len(player_pool) == 10:
        await ctx.send("10 players have joined.")
        team1, team2 = sort_players(player_pool)
        await display_teams(ctx, team1, team2)

# Function to sort players into roles and teams
def sort_players(players):
    tanks = []
    damage = []
    supports = []

    # Step 1: Assign players by their preferred roles
    for player in players:
        if player.preferred_role == "tank":
            tanks.append(player)
        elif player.preferred_role == "damage":
            damage.append(player)
        elif player.preferred_role == "support":
            supports.append(player)

    # Step 2: Fill missing roles with secondary roles if necessary
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

    # Step 3: Sort players by rank
    tanks = sorted(tanks, key=lambda p: p.rank, reverse=True)
    damage = sorted(damage, key=lambda p: p.rank, reverse=True)
    supports = sorted(supports, key=lambda p: p.rank, reverse=True)

    # Step 4: Assign players to teams, checking if there are enough players
    team1 = {
        "tank": [tanks[0]] if len(tanks) > 0 else [],
        "damage": [damage[0], damage[2]] if len(damage) > 2 else damage[:2],
        "support": [supports[0], supports[2]] if len(supports) > 2 else supports[:2]
    }

    team2 = {
        "tank": [tanks[1]] if len(tanks) > 1 else [],
        "damage": [damage[1], damage[3]] if len(damage) > 3 else damage[1:],
        "support": [supports[1], supports[3]] if len(supports) > 3 else supports[1:]
    }

    return team1, team2

# Function to display the teams in the Discord channel
async def display_teams(ctx, team1, team2):
    team1_str = "Team 1:\n"
    team2_str = "Team 2:\n"
    
    for role, players in team1.items():
        for player in players:
            team1_str += f"{player.battle_tag} ({role}) - Rank: {player.rank}\n"

    for role, players in team2.items():
        for player in players:
            team2_str += f"{player.battle_tag} ({role}) - Rank: {player.rank}\n"

    await ctx.send(f"**Teams for the PUG:**\n\n{team1_str}\n\n{team2_str}")

# Command to reset the PUG system (clear the player pool)
@bot.command()
async def reset_pug(ctx):
    global player_pool
    player_pool = []
    await ctx.send("The player pool has been reset. Ready for the next PUG!")

# Run the bot with your token
bot.run(TOKEN)