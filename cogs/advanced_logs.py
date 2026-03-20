import discord
from discord.ext import commands
import datetime

class AdvancedLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.db["settings"]

    async def get_log_channel(self, guild_id):
        data = await self.settings.find_one({"guild_id": guild_id})
        if data and "log_channel_id" in data:
            return self.bot.get_channel(data["log_channel_id"])
        return None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        log_channel = await self.get_log_channel(message.guild.id)
        if not log_channel: return

        embed = discord.Embed(title="🗑️ Message Deleted", description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}", color=discord.Color.red(), timestamp=datetime.datetime.now(datetime.UTC))
        embed.add_field(name="Content", value=message.content[:1024] or "[Image/Embed Only]", inline=False)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = await self.get_log_channel(before.guild.id)
        if not log_channel: return

        if before.roles != after.roles:
            added = [r.mention for r in after.roles if r not in before.roles]
            removed = [r.mention for r in before.roles if r not in after.roles]
            if added or removed:
                embed = discord.Embed(title="🛡️ Roles Updated", description=f"{before.mention}", color=discord.Color.purple(), timestamp=datetime.datetime.now(datetime.UTC))
                if added: embed.add_field(name="Added", value=" ".join(added))
                if removed: embed.add_field(name="Removed", value=" ".join(removed))
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = await self.get_log_channel(member.guild.id)
        if not log_channel: return

        if before.channel is None and after.channel is not None:
            await log_channel.send(embed=discord.Embed(title="🎙️ Voice Joined", description=f"{member.mention} joined {after.channel.mention}", color=discord.Color.green()))
        elif before.channel is not None and after.channel is None:
            await log_channel.send(embed=discord.Embed(title="🔇 Voice Left", description=f"{member.mention} left {before.channel.mention}", color=discord.Color.red()))

async def setup(bot):
    await bot.add_cog(AdvancedLogs(bot))
