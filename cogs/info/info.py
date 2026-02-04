import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import platform

class Info(commands.Cog):
    """ℹ️ Premium Bot Information Command"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_uptime_string(self) -> str:
        """Get formatted uptime string"""
        delta = datetime.now(timezone.utc) - self.bot.start_time

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

    def create_info_embed(self, user) -> discord.Embed:
        """Create the premium info embed"""
        # Calculate stats
        total_users = len(set(self.bot.get_all_members()))
        total_servers = len(self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        total_commands = len([c for c in self.bot.walk_commands()])
        uptime = self.get_uptime_string()
        latency = round(self.bot.latency * 1000)
        created_ts = int(self.bot.user.created_at.timestamp())

        embed = discord.Embed(
            title=f"✨ {self.bot.user.name} | Premium Bot",
            description=(
                f"*A premium Discord bot built with passion and precision.*\n\n"
                f"```\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"       🌟 PREMIUM BOT v{self.bot.version} 🌟\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"```"
            ),
            color=0x5865F2,
            timestamp=datetime.now(timezone.utc)
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # ═══════════════════════════════════════
        # Bot Identity
        # ═══════════════════════════════════════
        identity_info = (
            f"**Name:** {self.bot.user.name}\n"
            f"**ID:** `{self.bot.user.id}`\n"
            f"**Tag:** {self.bot.user}\n"
            f"**Version:** `{self.bot.version}`"
        )

        embed.add_field(
            name="🤖 Identity",
            value=identity_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Developer Info
        # ═══════════════════════════════════════
        dev_info = (
            f"**Developer:** {self.bot.developer}\n"
            f"**Framework:** discord.py\n"
            f"**Language:** Python\n"
            f"**License:** MIT"
        )

        embed.add_field(
            name="👨‍💻 Developer",
            value=dev_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Statistics
        # ═══════════════════════════════════════
        stats_info = (
            f"**Servers:** `{total_servers:,}`\n"
            f"**Users:** `{total_users:,}`\n"
            f"**Channels:** `{total_channels:,}`\n"
            f"**Commands:** `{total_commands}`"
        )

        embed.add_field(
            name="📊 Statistics",
            value=stats_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Performance
        # ═══════════════════════════════════════
        if latency < 100:
            ping_indicator = "🟢"
        elif latency < 200:
            ping_indicator = "🟡"
        else:
            ping_indicator = "🔴"

        perf_info = (
            f"**Latency:** `{latency}ms` {ping_indicator}\n"
            f"**Uptime:** `{uptime}`\n"
            f"**Shard:** `{self.bot.shard_id or 0}`\n"
            f"**Status:** 🟢 Online"
        )

        embed.add_field(
            name="⚡ Performance",
            value=perf_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Technical
        # ═══════════════════════════════════════
        tech_info = (
            f"**Python:** `{platform.python_version()}`\n"
            f"**discord.py:** `{discord.__version__}`\n"
            f"**Platform:** `{platform.system()}`\n"
            f"**Prefix:** `!` or `/`"
        )

        embed.add_field(
            name="🛠️ Technical",
            value=tech_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Dates
        # ═══════════════════════════════════════
        dates_info = (
            f"**Created:**\n\n"
            f"**Age:**\n"
        )

        embed.add_field(
            name="📅 Bot Created",
            value=dates_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Links Section
        # ═══════════════════════════════════════
        bot_id = self.bot.user.id
        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot%20applications.commands"

        links_info = (
            f"[🔗 Invite Bot]({invite_url})\n"
            f"[💬 Support Server]({self.bot.support_server})\n"
            f"[📂 GitHub]({self.bot.github})"
        )

        embed.add_field(
            name="🌐 Links",
            value=links_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Features
        # ═══════════════════════════════════════
        features_info = (
            "✅ Slash Commands\n"
            "✅ Prefix Commands\n"
            "✅ Premium Embeds\n"
            "✅ 24/7 Uptime"
        )

        embed.add_field(
            name="✨ Features",
            value=features_info,
            inline=True
        )

        embed.set_footer(
            text=f"Requested by {user.name} • Premium Bot",
            icon_url=user.display_avatar.url
        )

        # Set banner image if the bot has one
        if self.bot.user.banner:
            embed.set_image(url=self.bot.user.banner.url)

        return embed

    @app_commands.command(name="info", description="ℹ️ Display detailed bot information")
    async def info_slash(self, interaction: discord.Interaction):
        embed = self.create_info_embed(interaction.user)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="info", aliases=["about", "botinfo", "bot", "stats"])
    async def info_prefix(self, ctx: commands.Context):
        """ℹ️ Display detailed bot information"""
        embed = self.create_info_embed(ctx.author)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))