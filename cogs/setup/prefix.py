import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import json
import os
from config import Colors, Emojis

class PrefixCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/prefixes.json'
        self.prefixes = self.load_prefixes()

    def load_prefixes(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_prefixes(self):
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.prefixes, f, indent=4)

    @app_commands.command(name="setup-prefix", description="Set a custom prefix for this server")
    @app_commands.describe(prefix="The new prefix (1-5 characters)")
    @app_commands.guild_only()
    async def setup_prefix_slash(self, interaction: discord.Interaction, prefix: str):
        if interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Only the server owner can change the prefix.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if len(prefix) > 5 or len(prefix) < 1:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Prefix must be 1-5 characters.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        self.prefixes[str(interaction.guild.id)] = prefix
        self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Prefix Updated", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Server prefix has been changed to `{prefix}`"
        embed.set_footer(text=f"Changed by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reset-prefix", description="Reset the prefix to default")
    @app_commands.guild_only()
    async def reset_prefix_slash(self, interaction: discord.Interaction):
        if interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Only the server owner can reset the prefix.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if str(interaction.guild.id) in self.prefixes:
            del self.prefixes[str(interaction.guild.id)]
            self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Prefix Reset", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Server prefix has been reset to `{self.bot.default_prefix}`"
        embed.set_footer(text=f"Reset by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed)

    @commands.command(name="setup-prefix", aliases=["setprefix"])
    @commands.guild_only()
    async def setup_prefix_cmd(self, ctx, prefix: str = None):
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Only the server owner can change the prefix.")
            return await ctx.send(embed=embed)
        
        if prefix is None:
            current = self.prefixes.get(str(ctx.guild.id), self.bot.default_prefix)
            embed = discord.Embed(color=Colors.MAIN, description=f"Current prefix is `{current}`")
            return await ctx.send(embed=embed)
        
        if len(prefix) > 5:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Prefix must be 5 characters or less.")
            return await ctx.send(embed=embed)
        
        self.prefixes[str(ctx.guild.id)] = prefix
        self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Prefix changed to `{prefix}`")
        await ctx.send(embed=embed)

    @commands.command(name="reset-prefix")
    @commands.guild_only()
    async def reset_prefix_cmd(self, ctx):
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Only the server owner can reset the prefix.")
            return await ctx.send(embed=embed)
        
        if str(ctx.guild.id) in self.prefixes:
            del self.prefixes[str(ctx.guild.id)]
            self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Prefix reset to `{self.bot.default_prefix}`")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PrefixCog(bot))