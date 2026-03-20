import discord
from discord.ext import commands, tasks
import datetime

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.db["settings"]
        self.temp_roles_db = bot.db["temp_roles"]
        self.check_temp_roles.start()

    def cog_unload(self):
        self.check_temp_roles.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await self.settings.find_one({"guild_id": member.guild.id})
        if config and "auto_role_id" in config:
            role = member.guild.get_role(config["auto_role_id"])
            if role:
                try: await member.add_roles(role, reason="Auto-Role")
                except discord.Forbidden: pass

    @tasks.loop(minutes=1)
    async def check_temp_roles(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now(datetime.UTC)
        async for record in self.temp_roles_db.find({"expires_at": {"$lte": now}}):
            guild = self.bot.get_guild(record["guild_id"])
            if guild:
                member = guild.get_member(record["user_id"])
                role = guild.get_role(record["role_id"])
                if member and role:
                    try: await member.remove_roles(role, reason="Temp Role Expired")
                    except discord.Forbidden: pass
            await self.temp_roles_db.delete_one({"_id": record["_id"]})

async def setup(bot):
    await bot.add_cog(Roles(bot))
