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

    def get_prefix(self, guild_id):
        return self.prefixes.get(str(guild_id), self.bot.default_prefix)

    # Check if user is server owner
    def is_owner():
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == interaction.guild.owner_id
        return app_commands.check(predicate)

    @app_commands.command(name="setup-prefix", description="Set a custom prefix for this server")
    @app_commands.describe(prefix="The new prefix (1-5 characters)")
    @app_commands.guild_only()
    async def setup_prefix_slash(self, interaction: discord.Interaction, prefix: str):
        # Check if owner
        if interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Only the server owner can change the prefix."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Validate prefix
        if len(prefix) > 5:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Prefix must be 5 characters or less."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if len(prefix) < 1:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Prefix must be at least 1 character."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Save prefix
        self.prefixes[str(interaction.guild.id)] = prefix
        self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Prefix Updated", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Server prefix has been changed to `{prefix}`"
        embed.add_field(name="Example", value=f"`{prefix}ping` or `{prefix}help`", inline=False)
        embed.set_footer(text=f"Changed by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reset-prefix", description="Reset the prefix to default")
    @app_commands.guild_only()
    async def reset_prefix_slash(self, interaction: discord.Interaction):
        # Check if owner
        if interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Only the server owner can reset the prefix."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Remove custom prefix
        if str(interaction.guild.id) in self.prefixes:
            del self.prefixes[str(interaction.guild.id)]
            self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Prefix Reset", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Server prefix has been reset to `{self.bot.default_prefix}`"
        embed.add_field(name="Example", value=f"`{self.bot.default_prefix}ping` or `{self.bot.default_prefix}help`", inline=False)
        embed.set_footer(text=f"Reset by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed)

    @commands.command(name="setup-prefix", aliases=["setprefix", "prefix"])
    @commands.guild_only()
    async def setup_prefix_cmd(self, ctx, prefix: str = None):
        # Check if owner
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Only the server owner can change the prefix."
            )
            return await ctx.send(embed=embed)
        
        if prefix is None:
            current = self.get_prefix(ctx.guild.id)
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Current Prefix", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"The current prefix is `{current}`"
            embed.add_field(name="Change it", value=f"`{current}setup-prefix <new prefix>`", inline=False)
            return await ctx.send(embed=embed)
        
        # Validate prefix
        if len(prefix) > 5:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Prefix must be 5 characters or less."
            )
            return await ctx.send(embed=embed)
        
        # Save prefix
        self.prefixes[str(ctx.guild.id)] = prefix
        self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Prefix Updated", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Server prefix has been changed to `{prefix}`"
        embed.add_field(name="Example", value=f"`{prefix}ping` or `{prefix}help`", inline=False)
        embed.set_footer(text=f"Changed by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)

    @commands.command(name="reset-prefix", aliases=["resetprefix"])
    @commands.guild_only()
    async def reset_prefix_cmd(self, ctx):
        # Check if owner
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                color=Colors.ERROR,
                description=f"{Emojis.CROSS} Only the server owner can reset the prefix."
            )
            return await ctx.send(embed=embed)
        
        # Remove custom prefix
        if str(ctx.guild.id) in self.prefixes:
            del self.prefixes[str(ctx.guild.id)]
            self.save_prefixes()
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Prefix Reset", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Server prefix has been reset to `{self.bot.default_prefix}`"
        embed.add_field(name="Example", value=f"`{self.bot.default_prefix}ping` or `{self.bot.default_prefix}help`", inline=False)
        embed.set_footer(text=f"Reset by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PrefixCog(bot))