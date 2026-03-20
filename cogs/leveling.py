import discord
from discord.ext import commands
from discord import app_commands
import math

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = bot.db["levels"]

    def calc_level(self, xp): return int(0.1 * math.sqrt(xp))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        await self.levels.update_one({"user_id": message.author.id, "guild_id": message.guild.id}, {"$inc": {"xp": 5}}, upsert=True)

    @app_commands.command(name="rank", description="Check your rank.")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        data = await self.levels.find_one({"user_id": target.id, "guild_id": interaction.guild.id})
        xp = data["xp"] if data else 0
        
        embed = discord.Embed(title=f"{target.display_name}'s Rank", color=discord.Color.blue())
        embed.add_field(name="Level", value=str(self.calc_level(xp)))
        embed.add_field(name="XP", value=str(xp))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
