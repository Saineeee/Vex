import discord
from discord.ext import commands
from discord import app_commands

class TempVCControls(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.temp_vcs = bot.db["temp_vcs"]

    async def get_vc(self, interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You are not in a voice channel.", ephemeral=True)
            return None
        vc = interaction.user.voice.channel
        data = await self.temp_vcs.find_one({"channel_id": vc.id})
        if not data or data["owner_id"] != interaction.user.id:
            await interaction.response.send_message("❌ You don't own this VC.", ephemeral=True)
            return None
        return vc

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger, custom_id="vc_lock", emoji="🔒")
    async def lock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = await self.get_vc(interaction)
        if vc:
            await vc.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.response.send_message("Locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success, custom_id="vc_unlock", emoji="🔓")
    async def unlock_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = await self.get_vc(interaction)
        if vc:
            await vc.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.response.send_message("Unlocked.", ephemeral=True)

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = bot.db["settings"]
        self.temp_vcs = bot.db["temp_vcs"]
        # ⚡ Bolt: Cache settings to prevent DB queries in high-frequency listeners
        self._settings_cache = {}

    @app_commands.command(name="setuptempvc", description="[ADMIN] Setup temporary voice channels.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setuptempvc(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        category = await interaction.guild.create_category("⏳ TEMPORARY VOICE")
        dash = await interaction.guild.create_text_channel("🎛️・vc-dashboard", category=category)
        join_vc = await interaction.guild.create_voice_channel("➕ Join to Create", category=category)

        await self.settings.update_one({"guild_id": interaction.guild.id}, {"$set": {"temp_vc_join": join_vc.id, "temp_vc_category": category.id}}, upsert=True)

        # ⚡ Bolt: Update cache after writing to DB so listeners get fresh data immediately
        if interaction.guild.id not in self._settings_cache:
            # Fetch existing settings to ensure cache consistency with the database document
            existing = await self.settings.find_one({"guild_id": interaction.guild.id})
            self._settings_cache[interaction.guild.id] = existing or {}

        self._settings_cache[interaction.guild.id]["temp_vc_join"] = join_vc.id
        self._settings_cache[interaction.guild.id]["temp_vc_category"] = category.id

        await dash.send(embed=discord.Embed(title="VC Dashboard", description="Join ➕ Join to Create to get your own channel!"), view=TempVCControls(self.bot))
        await interaction.followup.send("System ready!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return

        # ⚡ Bolt: Use in-memory cache to skip DB query on voice state update
        guild_id = member.guild.id
        if guild_id not in self._settings_cache:
            settings = await self.settings.find_one({"guild_id": guild_id})
            if settings:
                self._settings_cache[guild_id] = settings
            else:
                # Cache negative result temporarily or just return to avoid repeated missing queries
                # We'll just cache an empty dict if not found
                self._settings_cache[guild_id] = {}

        settings = self._settings_cache.get(guild_id, {})
        if not settings or "temp_vc_join" not in settings: return

        if after.channel and after.channel.id == settings["temp_vc_join"]:
            category = member.guild.get_channel(settings["temp_vc_category"])
            new_vc = await member.guild.create_voice_channel(name=f"{member.display_name}'s VC", category=category)
            await member.move_to(new_vc)
            await self.temp_vcs.insert_one({"channel_id": new_vc.id, "owner_id": member.id})

        if before.channel:
            if await self.temp_vcs.find_one({"channel_id": before.channel.id}):
                if len(before.channel.members) == 0:
                    try:
                        await before.channel.delete()
                        await self.temp_vcs.delete_one({"channel_id": before.channel.id})
                    except: pass

async def setup(bot):
    await bot.add_cog(TempVoice(bot))
