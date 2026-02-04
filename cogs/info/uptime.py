import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import platform

# Optional: System monitoring
try:
    import psutil
    import os
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class Uptime(commands.Cog):
    """⏱️ Premium Uptime Monitor with system statistics"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_uptime(self) -> dict:
        """Calculate detailed uptime"""
        now = datetime.now(timezone.utc)
        delta = now - self.bot.start_time

        total_seconds = int(delta.total_seconds())
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds,
            'total_hours': (days * 24) + hours
        }

    def create_bar(self, value: float, max_val: float, length: int = 10) -> str:
        """Create a progress bar"""
        if max_val == 0:
            percentage = 0
        else:
            percentage = min(value / max_val, 1.0)

        filled = int(length * percentage)
        empty = length - filled
        return '█' * filled + '░' * empty

    def get_status(self, total_hours: int) -> tuple:
        """Get status based on uptime"""
        if total_hours < 1:
            return '🔴', 'Just Started', 0xFF4444
        elif total_hours < 24:
            return '🟡', 'Warming Up', 0xFFAA00
        elif total_hours < 72:
            return '🟢', 'Stable', 0x44FF44
        elif total_hours < 168:
            return '💚', 'Very Stable', 0x00FF88
        else:
            return '💎', 'Rock Solid', 0x00FFFF

    def get_milestone(self, total_hours: int) -> str:
        """Get current milestone"""
        if total_hours >= 720:
            return "🏆 **30 Day Champion**"
        elif total_hours >= 168:
            return "⭐ **Week Warrior**"
        elif total_hours >= 72:
            return "🎯 **72 Hour Hero**"
        elif total_hours >= 24:
            return "✨ **24 Hour Club**"
        else:
            remaining = 24 - total_hours
            return f"⏳ Next: **{remaining}h** to 24h Club"

    def get_system_stats(self) -> dict:
        """Get system statistics"""
        if not PSUTIL_AVAILABLE:
            return None
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            proc = psutil.Process(os.getpid())
            bot_mem = proc.memory_info().rss / (1024 ** 2)

            return {
                'cpu': cpu,
                'memory': mem.percent,
                'bot_memory': bot_mem
            }
        except:
            return None

    def create_uptime_embed(self, user) -> discord.Embed:
        """Create the premium uptime embed"""
        uptime = self.get_uptime()
        start_ts = int(self.bot.start_time.timestamp())

        emoji, status_text, color = self.get_status(uptime['total_hours'])

        embed = discord.Embed(
            title=f"{emoji} Premium Uptime Monitor",
            description="*Real-time system monitoring and uptime tracking*",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # ═══════════════════════════════════════
        # Main Uptime Display
        # ═══════════════════════════════════════
        uptime_box = (
            f"```\n"
            f"╔════════════════════════════════════╗\n"
            f"║  {uptime['days']:03d} Days  {uptime['hours']:02d} Hrs  {uptime['minutes']:02d} Min  {uptime['seconds']:02d} Sec  ║\n"
            f"╚════════════════════════════════════╝\n"
            f"```"
        )

        embed.add_field(
            name="⏱️ Current Uptime",
            value=uptime_box,
            inline=False
        )

        # ═══════════════════════════════════════
        # Session Info
        # ═══════════════════════════════════════
        session_info = (
            f"**Started:** \n"
            f"**Relative:** \n"
            f"**Status:** {emoji} {status_text}"
        )

        embed.add_field(
            name="🚀 Session Info",
            value=session_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Performance
        # ═══════════════════════════════════════
        latency = round(self.bot.latency * 1000)

        if latency < 100:
            ping_status = "🟢"
        elif latency < 200:
            ping_status = "🟡"
        else:
            ping_status = "🔴"

        perf_info = (
            f"**Latency:** `{latency}ms` {ping_status}\n"
            f"**Servers:** `{len(self.bot.guilds):,}`\n"
            f"**Users:** `{len(set(self.bot.get_all_members())):,}`"
        )

        embed.add_field(
            name="⚡ Performance",
            value=perf_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Progress Tracking
        # ═══════════════════════════════════════
        daily_bar = self.create_bar(uptime['hours'], 24, 8)
        weekly_bar = self.create_bar(uptime['days'] % 7, 7, 8)
        monthly_bar = self.create_bar(uptime['days'] % 30, 30, 8)

        progress_info = (
            f"**24h:** `{daily_bar}` {uptime['hours']}/24h\n"
            f"**7d:** `{weekly_bar}` {uptime['days'] % 7}/7d\n"
            f"**30d:** `{monthly_bar}` {uptime['days'] % 30}/30d"
        )

        embed.add_field(
            name="📊 Progress",
            value=progress_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # System Stats (if available)
        # ═══════════════════════════════════════
        stats = self.get_system_stats()
        if stats:
            cpu_bar = self.create_bar(stats['cpu'], 100, 6)
            mem_bar = self.create_bar(stats['memory'], 100, 6)

            system_info = (
                f"**CPU:** `{cpu_bar}` {stats['cpu']:.1f}%\n"
                f"**RAM:** `{mem_bar}` {stats['memory']:.1f}%\n"
                f"**Bot:** `{stats['bot_memory']:.1f} MB`"
            )

            embed.add_field(
                name="🖥️ System",
                value=system_info,
                inline=True
            )

        # ═══════════════════════════════════════
        # Achievements
        # ═══════════════════════════════════════
        milestone = self.get_milestone(uptime['total_hours'])
        uptime_pct = min((uptime['total_seconds'] / (30 * 24 * 3600)) * 100, 100)
        uptime_bar = self.create_bar(uptime_pct, 100, 8)

        achievement_info = (
            f"{milestone}\n\n"
            f"**Monthly:**\n`{uptime_bar}` {uptime_pct:.1f}%"
        )

        embed.add_field(
            name="🏆 Achievements",
            value=achievement_info,
            inline=True
        )

        # ═══════════════════════════════════════
        # Technical
        # ═══════════════════════════════════════
        tech_info = (
            f"**Python:** `{platform.python_version()}`\n"
            f"**discord.py:** `{discord.__version__}`\n"
            f"**OS:** `{platform.system()}`"
        )

        embed.add_field(
            name="🛠️ Technical",
            value=tech_info,
            inline=True
        )

        embed.set_footer(
            text=f"Requested by {user.name} • Premium Bot",
            icon_url=user.display_avatar.url
        )

        return embed

    @app_commands.command(name="uptime", description="⏱️ Check bot uptime with detailed statistics")
    async def uptime_slash(self, interaction: discord.Interaction):
        embed = self.create_uptime_embed(interaction.user)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="uptime", aliases=["up", "status", "runtime"])
    async def uptime_prefix(self, ctx: commands.Context):
        """⏱️ Check bot uptime with detailed statistics"""
        embed = self.create_uptime_embed(ctx.author)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Uptime(bot))