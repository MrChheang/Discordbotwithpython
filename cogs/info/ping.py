import discord
from discord.ext import commands
from discord import app_commands
import time

class Ping(commands.Cog):
    """Ping command to check bot latency"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Slash command: /ping
    @app_commands.command(name="ping", description="Check the bot's latency and response time")
    async def ping_slash(self, interaction: discord.Interaction):
        # Calculate latencies
        start_time = time.perf_counter()
        
        # Websocket latency
        ws_latency = round(self.bot.latency * 1000)
        
        # Create embed
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green() if ws_latency < 200 else discord.Color.orange()
        )
        
        embed.add_field(
            name="📡 Websocket Latency",
            value=f"`{ws_latency}ms`",
            inline=True
        )
        
        # Send initial response
        await interaction.response.send_message(embed=embed)
        
        # Calculate API latency
        end_time = time.perf_counter()
        api_latency = round((end_time - start_time) * 1000)
        
        embed.add_field(
            name="⚡ API Latency",
            value=f"`{api_latency}ms`",
            inline=True
        )
        
        # Add status indicator
        if ws_latency < 100:
            status = "🟢 Excellent"
        elif ws_latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 High Latency"
        
        embed.add_field(
            name="📊 Status",
            value=status,
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.edit_original_response(embed=embed)

    # Prefix command: !ping
    @commands.command(name="ping", help="Check the bot's latency and response time")
    async def ping_prefix(self, ctx: commands.Context):
        start_time = time.perf_counter()
        
        # Websocket latency
        ws_latency = round(self.bot.latency * 1000)
        
        # Create embed
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green() if ws_latency < 200 else discord.Color.orange()
        )
        
        embed.add_field(
            name="📡 Websocket Latency",
            value=f"`{ws_latency}ms`",
            inline=True
        )
        
        # Send initial response
        msg = await ctx.send(embed=embed)
        
        # Calculate API latency
        end_time = time.perf_counter()
        api_latency = round((end_time - start_time) * 1000)
        
        embed.add_field(
            name="⚡ API Latency",
            value=f"`{api_latency}ms`",
            inline=True
        )
        
        # Add status indicator
        if ws_latency < 100:
            status = "🟢 Excellent"
        elif ws_latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 High Latency"
        
        embed.add_field(
            name="📊 Status",
            value=status,
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        
        await msg.edit(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))