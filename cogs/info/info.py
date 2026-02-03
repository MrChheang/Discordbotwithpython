import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import platform

class Info(commands.Cog):
    """Info command to display detailed bot information"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_uptime(self):
        """Calculate and format the bot's uptime"""
        now = datetime.now(timezone.utc)
        # start_time is already timezone-aware from main.py
        delta = now - self.bot.start_time

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

    def create_info_embed(self, user):
        """Create the bot info embed"""
        # Calculate stats
        total_users = len(set(self.bot.get_all_members()))
        total_servers = len(self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        uptime = self.get_uptime()
        latency = round(self.bot.latency * 1000)

        # Bot created date
        created_at = self.bot.user.created_at

        embed = discord.Embed(
            title=f"ℹ️ {self.bot.user.name} Information",
            description="Here's everything you need to know about me!",
            color=discord.Color.blurple()
        )

        # Set bot avatar as thumbnail
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Bot Info Section
        embed.add_field(
            name="🤖 Bot Info",
            value=f"**Name:** {self.bot.user.name}\n"
                  f"**ID:** `{self.bot.user.id}`\n"
                  f"**Developer:** {self.bot.developer}",
            inline=True
        )

        # Statistics Section
        embed.add_field(
            name="📊 Statistics",
            value=f"**Servers:** {total_servers:,}\n"
                  f"**Users:** {total_users:,}\n"
                  f"**Channels:** {total_channels:,}",
            inline=True
        )

        # Performance Section
        embed.add_field(
            name="⚡ Performance",
            value=f"**Ping:** {latency}ms\n"
                  f"**Uptime:** {uptime}\n"
                  f"**Python:** {platform.python_version()}",
            inline=True
        )

        # Technical Info Section
        embed.add_field(
            name="🛠️ Technical",
            value=f"**discord.py:** {discord.__version__}\n"
                  f"**Platform:** {platform.system()}\n"
                  f"**Prefix:** `!` or `/`",
            inline=True
        )

        # Bot Created Section
        embed.add_field(
            name="📅 Bot Created",
            value=f"\n"
                  f"()",
            inline=True
        )

        # Links Section (customize these)
        embed.add_field(
            name="🔗 Links",
            value="[Invite Bot](https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot%20applications.commands)\n"
                  "[Support Server](https://discord.gg/your-server)\n"
                  "[GitHub](https://github.com/your-repo)",
            inline=True
        )

        embed.set_footer(
            text=f"Requested by {user.name} • Made with ❤️ using discord.py",
            icon_url=user.display_avatar.url
        )
        embed.timestamp = datetime.now(timezone.utc)

        return embed

    # Slash command: /info
    @app_commands.command(name="info", description="Display detailed information about the bot")
    async def info_slash(self, interaction: discord.Interaction):
        embed = self.create_info_embed(interaction.user)
        await interaction.response.send_message(embed=embed)

    # Prefix command: !info
    @commands.command(name="info", aliases=["botinfo", "about"], help="Display detailed information about the bot")
    async def info_prefix(self, ctx: commands.Context):
        embed = self.create_info_embed(ctx.author)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))