import discord
from discord.ext import commands
from discord import app_commands
import time
from datetime import datetime, timezone
from config import Colors, Emojis

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_status(self, ms):
        if ms < 80: return "Excellent"
        elif ms < 150: return "Good"
        elif ms < 250: return "Okay"
        return "Slow"

    def make_bar(self, ms):
        bars = min(int(ms / 30), 10)
        return "▰" * bars + "▱" * (10 - bars)

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping_slash(self, interaction: discord.Interaction):
        start = time.perf_counter()
        await interaction.response.defer()
        api = round((time.perf_counter() - start) * 1000)
        ws = round(self.bot.latency * 1000)
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Pong!", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Websocket", value=f"```{ws}ms```", inline=True)
        embed.add_field(name="API", value=f"```{api}ms```", inline=True)
        embed.add_field(name="Status", value=f"```{self.get_status(ws)}```", inline=True)
        embed.add_field(name="Latency", value=f"`{self.make_bar(ws)}` {ws}ms", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.followup.send(embed=embed)

    @commands.command(name="ping", aliases=["p"])
    async def ping_prefix(self, ctx):
        start = time.perf_counter()
        msg = await ctx.send("Pinging...")
        api = round((time.perf_counter() - start) * 1000)
        ws = round(self.bot.latency * 1000)
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Pong!", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Websocket", value=f"```{ws}ms```", inline=True)
        embed.add_field(name="API", value=f"```{api}ms```", inline=True)
        embed.add_field(name="Status", value=f"```{self.get_status(ws)}```", inline=True)
        embed.add_field(name="Latency", value=f"`{self.make_bar(ws)}` {ws}ms", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await msg.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))