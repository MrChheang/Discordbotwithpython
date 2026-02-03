import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

class Uptime(commands.Cog):
    """Uptime command to check how long the bot has been running"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_uptime(self):
        """Calculate and format the bot's uptime"""
        now = datetime.now(timezone.utc)
        start_time = self.bot.start_time.replace(tzinfo=timezone.utc)
        delta = now - start_time
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)

    def create_uptime_embed(self, user):
        """Create the uptime embed"""
        uptime = self.get_uptime()
        start_time = self.bot.start_time.replace(tzinfo=timezone.utc)
        
        embed = discord.Embed(
            title="⏱️ Bot Uptime",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🕐 Current Uptime",
            value=f"`{uptime}`",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Started At",
            value=f"",
            inline=True
        )
        
        embed.add_field(
            name="📅 Relative",
            value=f"",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {user.name}", icon_url=user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        return embed

    # Slash command: /uptime
    @app_commands.command(name="uptime", description="Check how long the bot has been running")
    async def uptime_slash(self, interaction: discord.Interaction):
        embed = self.create_uptime_embed(interaction.user)
        await interaction.response.send_message(embed=embed)

    # Prefix command: !uptime
    @commands.command(name="uptime", help="Check how long the bot has been running")
    async def uptime_prefix(self, ctx: commands.Context):
        embed = self.create_uptime_embed(ctx.author)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Uptime(bot))