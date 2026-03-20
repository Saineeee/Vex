import discord
from discord.ext import commands
from discord import app_commands
import io

class TicketControls(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None) 
        self.bot = bot

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds...", ephemeral=False)
        messages = [f"[{m.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {m.author.name}: {m.content}" async for m in interaction.channel.history(limit=None, oldest_first=True)]
        
        transcript = discord.File(io.StringIO("\n".join(messages)), filename=f"{interaction.channel.name}.txt")
        settings = await self.bot.db["settings"].find_one({"guild_id": interaction.guild.id})
        
        if settings and "log_channel_id" in settings:
            log_channel = interaction.guild.get_channel(settings["log_channel_id"])
            if log_channel: await log_channel.send(f"Ticket closed: {interaction.channel.name}", file=transcript)

        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketPanel(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Open a Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_btn", emoji="📩")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        category = discord.utils.get(interaction.guild.categories, name="🎫 Support Tickets")
        if not category: category = await interaction.guild.create_category("🎫 Support Tickets")

        ticket_name = f"ticket-{interaction.user.name.lower()}"
        if discord.utils.get(category.channels, name=ticket_name):
            return await interaction.response.send_message("You already have an open ticket.", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        ticket_channel = await interaction.guild.create_text_channel(name=ticket_name, category=category, overwrites=overwrites)
        await ticket_channel.send(f"{interaction.user.mention} Support will be here shortly.", view=TicketControls(self.bot))
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setuptickets", description="[ADMIN] Spawn the ticket panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setuptickets(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Contact Support", description="Click below to open a ticket.", color=discord.Color.blue())
        await interaction.channel.send(embed=embed, view=TicketPanel(self.bot))
        await interaction.response.send_message("Deployed!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
