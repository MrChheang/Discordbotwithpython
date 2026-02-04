import discord
from discord.ext import commands
from discord import app_commands
import time
import asyncio
from datetime import datetime, timezone

class Ping(commands.Cog):
    """🏓 Premium Ping Command with detailed latency analysis"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_latency_color(self, latency: int) -> int:
        """Get color based on latency"""
        if latency < 50:
            return 0x00FF88  # Excellent - Cyan/Green
        elif latency < 100:
            return 0x44FF44  # Great - Green
        elif latency < 150:
            return 0xFFFF00  # Good - Yellow
        elif latency < 200:
            return 0xFFA500  # Moderate - Orange
        else:
            return 0xFF4444  # High - Red

    def get_latency_status(self, latency: int) -> tuple:
        """Get status emoji and text"""
        if latency < 50:
            return "⚡", "Exceptional", "Lightning fast response!"
        elif latency < 100:
            return "🟢", "Excellent", "Running smoothly!"
        elif latency < 150:
            return "🟡", "Good", "Normal performance"
        elif latency < 200:
            return "🟠", "Moderate", "Slight delay detected"
        else:
            return "🔴", "High", "Experiencing delays"

    def create_latency_bar(self, latency: int, max_latency: int = 300) -> str:
        """Create a visual latency bar"""
        percentage = min(latency / max_latency, 1.0)
        filled = int(10 * percentage)
        empty = 10 - filled

        if percentage < 0.33:
            bar = "🟩" * filled + "⬜" * empty
        elif percentage < 0.66:
            bar = "🟨" * filled + "⬜" * empty
        else:
            bar = "🟥" * filled + "⬜" * empty

        return bar

    async def create_ping_embed(self, user) -> discord.Embed:
        """Create the premium ping embed"""
        # Calculate latencies
        start = time.perf_counter()
        ws_latency = round(self.bot.latency * 1000)

        # Get status info
        emoji, status, description = self.get_latency_status(ws_latency)
        color = self.get_latency_color(ws_latency)

        embed = discord.Embed(
            title=f"{emoji} Pong! | Latency Analysis",
            description=f"*{description}*",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # ═══════════════════════════════════════
        # Latency Display Box
        # ═══════════════════════════════════════
        latency_box = (
            f"```\n"
            f"┌────────────────────────────┐\n"
            f"│   🏓 LATENCY: {ws_latency:>4}ms        │\n"
            f"└────────────────────────────┘\n"
            f"```"
        )

        embed.add_field(
            name="📡 Websocket Latency",
            value=latency_box,
            inline=False
        )

        # ═══════════════════════════════════════
        # Visual Latency Bar
        # ═══════════════════════════════════════
        latency_bar = self.create_latency_bar(ws_latency)

        bar_display = (
            f"{latency_bar}\n"
            f"`0ms` ━━━━━━━━━━━━━━ `300ms`"
        )

        embed.add_field(
            name="📊 Latency Visualization",
            value=bar_display,
            inline=False
        )

        # ═══════════════════════════════════════
        # Status & Details
        # ═══════════════════════════════════════
        status_display = (
            f"**Status:** {emoji} {status}\n"
            f"**Shard:** `{self.bot.shard_id or 0}`\n"
            f"**Servers:** `{len(self.bot.guilds):,}`"
        )

        embed.add_field(
            name="⚡ Connection Status",
            value=status_display,
            inline=True
        )

        # Latency Rating
        if ws_latency < 100:
            rating = "⭐⭐⭐⭐⭐"
            grade = "A+"
        elif ws_latency < 150:
            rating = "⭐⭐⭐⭐"
            grade = "A"
        elif ws_latency < 200:
            rating = "⭐⭐⭐"
            grade = "B"
        elif ws_latency < 250:
            rating = "⭐⭐"
            grade = "C"
        else:
            rating = "⭐"
            grade = "D"

        rating_display = (
            f"**Grade:** `{grade}`\n"
            f"**Rating:** {rating}\n"
            f"**Quality:** {'Premium' if ws_latency < 100 else 'Standard'}"
        )

        embed.add_field(
            name="🎯 Performance Rating",
            value=rating_display,
            inline=True
        )

        # Timestamp info
        time_display = (
            f"**Checked:** \n"
            f"**Bot Uptime:** `Online`\n"
            f"**Region:** `Auto`"
        )

        embed.add_field(
            name="🕐 Timestamp",
            value=time_display,
            inline=True
        )

        embed.set_footer(
            text=f"Requested by {user.name} • Premium Ping Monitor",
            icon_url=user.display_avatar.url
        )

        return embed

    @app_commands.command(name="ping", description="🏓 Check bot latency with detailed analysis")
    async def ping_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await self.create_ping_embed(interaction.user)

        # Calculate API latency
        start = time.perf_counter()
        await interaction.followup.send(embed=embed)
        api_latency = round((time.perf_counter() - start) * 1000)

        # Update embed with API latency
        embed.add_field(
            name="🌐 API Response",
            value=f"```{api_latency}ms```",
            inline=True
        )

        await interaction.edit_original_response(embed=embed)

    @commands.command(name="ping", aliases=["p", "latency", "pong"])
    async def ping_prefix(self, ctx: commands.Context):
        """🏓 Check bot latency with detailed analysis"""
        async with ctx.typing():
            embed = await self.create_ping_embed(ctx.author)

        start = time.perf_counter()
        msg = await ctx.send(embed=embed)
        api_latency = round((time.perf_counter() - start) * 1000)

        embed.add_field(
            name="🌐 API Response",
            value=f"```{api_latency}ms```",
            inline=True
        )

        await msg.edit(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))