import discord
from discord.ext import commands, tasks
from discord import app_commands

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.db["settings"]
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @app_commands.command(name="setupstats", description="[ADMIN] Create auto-updating stat channels.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setupstats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(connect=False)}
        category = await guild.create_category("📊 Server Stats", overwrites=overwrites, position=0)
        
        total_vc = await guild.create_voice_channel(f"Members: {guild.member_count}", category=category)
        await self.settings.update_one({"guild_id": guild.id}, {"$set": {"stats_category": category.id, "stats_total": total_vc.id}}, upsert=True)
        await interaction.followup.send("Stats channel created!")

    @tasks.loop(minutes=10)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        async for data in self.settings.find({"stats_category": {"$exists": True}}):
            guild = self.bot.get_guild(data["guild_id"])
            if not guild: continue
            
            total_vc = guild.get_channel(data.get("stats_total"))
            if total_vc and total_vc.name != f"Members: {guild.member_count}":
                try: await total_vc.edit(name=f"Members: {guild.member_count}")
                except: pass

async def setup(bot):
    await bot.add_cog(ServerStats(bot))
