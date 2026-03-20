import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! **{round(self.bot.latency * 1000)}ms**")

    @app_commands.command(name="serverinfo", description="View server stats.")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=g.name, color=discord.Color.blue())
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Created", value=g.created_at.strftime("%Y-%m-%d"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="[MOD] Create a simple poll.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def poll(self, interaction: discord.Interaction, question: str):
        await interaction.response.send_message("Creating...", ephemeral=True)
        msg = await interaction.channel.send(embed=discord.Embed(title="📊 Poll", description=f"**{question}**", color=discord.Color.gold()))
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

async def setup(bot):
    await bot.add_cog(Utility(bot))
