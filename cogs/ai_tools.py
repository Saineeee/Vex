import discord
from discord.ext import commands
from discord import app_commands
from groq import AsyncGroq
import os

class AITools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    @app_commands.command(name="summarize", description="[MOD] Summarize recent chat.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def summarize(self, interaction: discord.Interaction, amount: int = 50):
        await interaction.response.defer(ephemeral=True)
        messages = [f"{m.author.name}: {m.content}" async for m in interaction.channel.history(limit=min(amount, 100)) if not m.author.bot]
        messages.reverse()
        
        try:
            res = await self.groq.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": f"Summarize this chat in 3 bullet points:\n{chr(10).join(messages)}"}]
            )
            await interaction.followup.send(embed=discord.Embed(title="Summary", description=res.choices[0].message.content, color=discord.Color.purple()))
        except Exception:
            await interaction.followup.send("API Error.")

async def setup(bot):
    await bot.add_cog(AITools(bot))
