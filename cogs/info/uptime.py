import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

from config import Colors, Emojis


class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_uptime(self):
        now = datetime.now(timezone.utc)
        delta = now - self.bot.start_time
        
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)

    def get_timestamps(self):
        # Get unix timestamp as integer
        ts = int(self.bot.start_time.timestamp())
        return {
            "relative": f"<t:{ts}:R>",
            "full": f"<t:{ts}:F>"
        }

    @app_commands.command(name="uptime", description="Check how long the bot has been running")
    async def uptime_slash(self, interaction: discord.Interaction):
        uptime_str = self.format_uptime()
        timestamps = self.get_timestamps()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Uptime", icon_url=self.bot.user.display_avatar.url)
        
        embed.add_field(
            name="Running for",
            value=f"```{uptime_str}```",
            inline=True
        )
        embed.add_field(
            name="Since",
            value=timestamps["relative"],
            inline=True
        )
        embed.add_field(
            name="Started",
            value=timestamps["full"],
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed)

    @commands.command(name="uptime", aliases=["up"])
    async def uptime_prefix(self, ctx):
        uptime_str = self.format_uptime()
        timestamps = self.get_timestamps()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Uptime", icon_url=self.bot.user.display_avatar.url)
        
        embed.add_field(
            name="Running for",
            value=f"```{uptime_str}```",
            inline=True
        )
        embed.add_field(
            name="Since",
            value=timestamps["relative"],
            inline=True
        )
        embed.add_field(
            name="Started",
            value=timestamps["full"],
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Uptime(bot))