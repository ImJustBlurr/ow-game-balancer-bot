import os
from dotenv import load_dotenv
import discord
from typing import Literal
from discord.ext import commands
from player_sort import role_sort

load_dotenv()
TOKEN = os.getenv('TOKEN')

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='??', intents=intents)

# Initialize Slash Commands
@bot.event
async def on_ready():
    guild_id = 1281765355122987110
    guild = discord.Object(id=guild_id)

    # sets up the command tree
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

# Player class to store player info
class Player:
    def __init__(self, user_id, battle_tag, preferred_role, division, tier, sr, secondary_role):
        self.user_id = user_id
        self.battle_tag = battle_tag
        self.preferred_role = preferred_role.lower()
        self.division = division.lower()
        self.tier = tier
        self.sr = sr
        self.secondary_role = secondary_role.lower()

# Global player pool to store current PUG players
player_pool = []

# Conversion dictionary for ow2 rank to SR
conversion = {
    "Champion1": 4400,
    "Champion2": 4300,
    "Champion3": 4200,
    "Champion4": 4100,
    "Champion5": 4000,
    "Grandmaster1": 4400,
    "Grandmaster2": 4300,
    "Grandmaster3": 4200,
    "Grandmaster4": 4100,
    "Grandmaster5": 4000,
    "Master1": 3900,
    "Master2": 3800,
    "Master3": 3700,
    "Master4": 3600,
    "Master5": 3500,
    "Diamond1": 3400,
    "Diamond2": 3300,
    "Diamond3": 3200,
    "Diamond4": 3100,
    "Diamond5": 3000,
    "Platinum1": 2900,
    "Platinum2": 2800,
    "Platinum3": 2700,
    "Platinum4": 2600,
    "Platinum5": 2500,
    "Gold1": 2400,
    "Gold2": 2300,
    "Gold3": 2200,
    "Gold4": 2100,
    "Gold5": 2000,
    "Silver1": 1900,
    "Silver2": 1800,
    "Silver3": 1700,
    "Silver4": 1600,
    "Silver5": 1500,
    "Bronze1": 1500,
    "Bronze2": 1100,
    "Bronze3": 750,
    "Bronze4": 370,
    "Bronze5": 0
}

# Dictionary to hold players based on role preferences
roles_needed = {
    "tank": 2,
    "damage": 4,
    "support": 4
}

@bot.tree.command(name="join", description="Join the PUG")
async def join(interaction: discord.Interaction, 
               battletag: str, 
               role: Literal["Tank", "Damage", "Support"], 
               division: Literal["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Champion"], 
               tier: Literal["1", "2", "3", "4", "5"], 
               secondary_role: Literal["Tank", "Damage", "Support"]):

    if len(player_pool) >= 10:
        await interaction.response.send_message("Player pool is already full. Wait for the next game!", ephemeral=True)
        return
    
    rank = division + tier
    sr = conversion[rank]
    
    # Add player to the player pool
    user_id = interaction.user.id
    player = Player(user_id, battletag, role, division, tier, sr, secondary_role)
    player_pool.append(player)

    embed=discord.Embed(title=f"Joined! {len(player_pool)}/10", color=0x00ff00)
    embed.add_field(name="Battle Tag", value=player.battle_tag, inline=False)
    embed.add_field(name="Role", value=player.preferred_role.title(), inline=False)
    embed.add_field(name="Rank", value=f"{player.division.title()} {player.tier}", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=False)

    # Once 10 players are in the pool, sort and create teams
    if len(player_pool) == 10:
        await interaction.channel.send("10 players have joined. Generating teams...")
        team1, team2 = role_sort(player_pool, roles_needed)
        channel = interaction.channel_id
        await display_teams(channel, team1, team2)

# Function to display the teams
async def display_teams(channel_id, team1, team2):
    team1_str = ""
    team2_str = ""

    role_icons = {
        "tank": "🛡",
        "damage": "⚔️",
        "support": "💉"
    }
    
    summation = 0

    for role, players in team1.items():
        for player in players:
            team1_str += f"{role_icons[role]} {player.battle_tag} ({player.sr})\n"
            summation += player.sr

    team1_average = summation / 5

    summation = 0

    for role, players in team2.items():
        for player in players:
            team2_str += f"{role_icons[role]} {player.battle_tag} ({player.sr})\n"
            summation += player.sr

    team2_average = summation / 5

    embed=discord.Embed(title=f"Teams for the PUG:", color=0xFC9D1F)
    embed.add_field(name=f"Team 1 ({team1_average})", value=team1_str, inline=True)
    embed.add_field(name=f"Team 2 ({team2_average})", value=team2_str, inline=True)
    channel = bot.get_channel(channel_id)
    await channel.send(embed=embed)

# Command to reset the PUG system (clear the player pool)
@bot.command()
async def reset_pug(ctx):
    global player_pool
    player_pool = []
    await ctx.send("The player pool has been reset. Ready for the next PUG!")

# Run the bot with your token
bot.run(TOKEN)