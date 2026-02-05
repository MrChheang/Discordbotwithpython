import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
import json
import os
import re
from config import Colors, Emojis

class ModData:
    def __init__(self):
        self.data_folder = 'data/mod'
        os.makedirs(self.data_folder, exist_ok=True)
    
    def _get_path(self, guild_id, file):
        return f'{self.data_folder}/{guild_id}_{file}.json'
    
    def load(self, guild_id, file):
        try:
            with open(self._get_path(guild_id, file), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save(self, guild_id, file, data):
        with open(self._get_path(guild_id, file), 'w') as f:
            json.dump(data, f, indent=2)

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = ModData()

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @app_commands.default_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You cannot kick this member.", ephemeral=True)
        await member.kick(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been kicked.\nReason: {reason}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason")
    @app_commands.default_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You cannot ban this member.", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been banned.\nReason: {reason}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(user_id="User ID to unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{user}** has been unbanned.")
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("User not found or not banned.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member", duration="Duration (e.g., 1h, 30m, 1d)", reason="Reason")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason"):
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        match = re.match(r'^(\d+)([smhd])$', duration.lower())
        if not match:
            return await interaction.response.send_message("Invalid duration. Use: 30s, 5m, 1h, 1d", ephemeral=True)
        amount, unit = int(match.group(1)), match.group(2)
        seconds = amount * time_units[unit]
        await member.timeout(timedelta(seconds=seconds), reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** timed out for **{duration}**.\nReason: {reason}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-timeout", description="Remove timeout")
    @app_commands.describe(member="Member")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout_slash(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Timeout removed from **{member}**.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member", reason="Reason")
    @app_commands.default_permissions(moderate_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        warns = self.data.load(interaction.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        user_warns.append({'id': len(user_warns) + 1, 'reason': reason, 'mod': interaction.user.id, 'time': datetime.now(timezone.utc).isoformat()})
        warns[str(member.id)] = user_warns
        self.data.save(interaction.guild.id, 'warns', warns)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** warned.\nReason: {reason}\nTotal warns: {len(user_warns)}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="View warnings")
    @app_commands.describe(member="Member")
    @app_commands.default_permissions(moderate_members=True)
    async def warnings_slash(self, interaction: discord.Interaction, member: discord.Member):
        warns = self.data.load(interaction.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name=f"Warnings for {member}", icon_url=member.display_avatar.url)
        if not user_warns:
            embed.description = "No warnings."
        else:
            embed.description = "\n".join([f"**#{w['id']}** - {w['reason'][:50]}" for w in user_warns[-10:]])
            embed.set_footer(text=f"Total: {len(user_warns)}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mod-logs", description="Set mod logs channel")
    @app_commands.describe(channel="Channel")
    @app_commands.default_permissions(administrator=True)
    async def modlogs_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        settings = self.data.load(interaction.guild.id, 'settings')
        settings['log_channel'] = channel.id
        self.data.save(interaction.guild.id, 'settings', settings)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Mod logs set to {channel.mention}")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.kick(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** kicked. Reason: {reason}")
        await ctx.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.ban(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** banned. Reason: {reason}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))