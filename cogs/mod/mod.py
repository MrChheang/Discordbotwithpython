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

    def parse_duration(self, duration):
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        match = re.match(r'^(\d+)([smhd])$', duration.lower())
        if not match:
            return None
        amount, unit = int(match.group(1)), match.group(2)
        return amount * time_units[unit]

    # ═══════════════════════════════════════════════════════════
    # KICK COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(f"{Emojis.CROSS} You cannot kick this member.", ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(f"{Emojis.CROSS} I cannot kick this member.", ephemeral=True)
        await member.kick(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been kicked.\n**Reason:** {reason}")
        embed.set_footer(text=f"By {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{Emojis.CROSS} You cannot kick this member.")
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{Emojis.CROSS} I cannot kick this member.")
        await member.kick(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been kicked.\n**Reason:** {reason}")
        embed.set_footer(text=f"By {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # BAN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(f"{Emojis.CROSS} You cannot ban this member.", ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(f"{Emojis.CROSS} I cannot ban this member.", ephemeral=True)
        await member.ban(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been banned.\n**Reason:** {reason}")
        embed.set_footer(text=f"By {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{Emojis.CROSS} You cannot ban this member.")
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{Emojis.CROSS} I cannot ban this member.")
        await member.ban(reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been banned.\n**Reason:** {reason}")
        embed.set_footer(text=f"By {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # UNBAN COMMAND
    # ═══════════════════════════════════════════════════════════
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
            await interaction.response.send_message(f"{Emojis.CROSS} User not found or not banned.", ephemeral=True)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_prefix(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{user}** has been unbanned.")
            await ctx.send(embed=embed)
        except:
            await ctx.send(f"{Emojis.CROSS} User not found or not banned.")

    # ═══════════════════════════════════════════════════════════
    # TIMEOUT COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member to timeout", duration="Duration (e.g., 30s, 5m, 1h, 1d)", reason="Reason")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        seconds = self.parse_duration(duration)
        if not seconds:
            return await interaction.response.send_message(f"{Emojis.CROSS} Invalid duration. Use: 30s, 5m, 1h, 1d", ephemeral=True)
        await member.timeout(timedelta(seconds=seconds), reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** timed out for **{duration}**.\n**Reason:** {reason}")
        embed.set_footer(text=f"By {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="timeout", aliases=["mute", "to"])
    @commands.has_permissions(moderate_members=True)
    async def timeout_prefix(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        seconds = self.parse_duration(duration)
        if not seconds:
            return await ctx.send(f"{Emojis.CROSS} Invalid duration. Use: 30s, 5m, 1h, 1d")
        await member.timeout(timedelta(seconds=seconds), reason=reason)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** timed out for **{duration}**.\n**Reason:** {reason}")
        embed.set_footer(text=f"By {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # REMOVE TIMEOUT COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="remove-timeout", description="Remove timeout from a member")
    @app_commands.describe(member="Member to untimeout")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout_slash(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Timeout removed from **{member}**.")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="untimeout", aliases=["unmute", "removetimeout"])
    @commands.has_permissions(moderate_members=True)
    async def untimeout_prefix(self, ctx, member: discord.Member):
        await member.timeout(None)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Timeout removed from **{member}**.")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # WARN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for warning")
    @app_commands.default_permissions(moderate_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        warns = self.data.load(interaction.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        warn_id = len(user_warns) + 1
        user_warns.append({
            'id': warn_id,
            'reason': reason,
            'mod': interaction.user.id,
            'time': datetime.now(timezone.utc).isoformat()
        })
        warns[str(member.id)] = user_warns
        self.data.save(interaction.guild.id, 'warns', warns)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been warned.\n**Reason:** {reason}\n**Total Warnings:** {len(user_warns)}")
        embed.set_footer(text=f"By {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        warns = self.data.load(ctx.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        warn_id = len(user_warns) + 1
        user_warns.append({
            'id': warn_id,
            'reason': reason,
            'mod': ctx.author.id,
            'time': datetime.now(timezone.utc).isoformat()
        })
        warns[str(member.id)] = user_warns
        self.data.save(ctx.guild.id, 'warns', warns)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} **{member}** has been warned.\n**Reason:** {reason}\n**Total Warnings:** {len(user_warns)}")
        embed.set_footer(text=f"By {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # REMOVE WARN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="remove-warn", description="Remove a warning from a member")
    @app_commands.describe(member="Member", warn_id="Warning ID to remove")
    @app_commands.default_permissions(moderate_members=True)
    async def removewarn_slash(self, interaction: discord.Interaction, member: discord.Member, warn_id: int):
        warns = self.data.load(interaction.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        new_warns = [w for w in user_warns if w['id'] != warn_id]
        if len(new_warns) == len(user_warns):
            return await interaction.response.send_message(f"{Emojis.CROSS} Warning #{warn_id} not found.", ephemeral=True)
        warns[str(member.id)] = new_warns
        self.data.save(interaction.guild.id, 'warns', warns)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Warning #{warn_id} removed from **{member}**.")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="removewarn", aliases=["delwarn", "unwarn"])
    @commands.has_permissions(moderate_members=True)
    async def removewarn_prefix(self, ctx, member: discord.Member, warn_id: int):
        warns = self.data.load(ctx.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        new_warns = [w for w in user_warns if w['id'] != warn_id]
        if len(new_warns) == len(user_warns):
            return await ctx.send(f"{Emojis.CROSS} Warning #{warn_id} not found.")
        warns[str(member.id)] = new_warns
        self.data.save(ctx.guild.id, 'warns', warns)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Warning #{warn_id} removed from **{member}**.")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # WARNINGS COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="warnings", description="View member warnings")
    @app_commands.describe(member="Member to check")
    @app_commands.default_permissions(moderate_members=True)
    async def warnings_slash(self, interaction: discord.Interaction, member: discord.Member):
        warns = self.data.load(interaction.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name=f"Warnings for {member}", icon_url=member.display_avatar.url)
        if not user_warns:
            embed.description = "No warnings found."
        else:
            lines = []
            for w in user_warns[-10:]:
                lines.append(f"**#{w['id']}** - {w['reason'][:40]}")
            embed.description = "\n".join(lines)
            embed.set_footer(text=f"Total: {len(user_warns)} warnings")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings_prefix(self, ctx, member: discord.Member):
        warns = self.data.load(ctx.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name=f"Warnings for {member}", icon_url=member.display_avatar.url)
        if not user_warns:
            embed.description = "No warnings found."
        else:
            lines = []
            for w in user_warns[-10:]:
                lines.append(f"**#{w['id']}** - {w['reason'][:40]}")
            embed.description = "\n".join(lines)
            embed.set_footer(text=f"Total: {len(user_warns)} warnings")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # BLACKLIST COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="blacklist", description="View all users with warnings/bans")
    @app_commands.default_permissions(moderate_members=True)
    async def blacklist_slash(self, interaction: discord.Interaction):
        warns = self.data.load(interaction.guild.id, 'warns')
        embed = discord.Embed(color=Colors.MAIN, title="Server Blacklist")
        if not warns:
            embed.description = "No users with warnings."
        else:
            lines = []
            for user_id, user_warns in list(warns.items())[:15]:
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    lines.append(f"**{user}** - {len(user_warns)} warnings")
                except:
                    lines.append(f"Unknown ({user_id}) - {len(user_warns)} warnings")
            embed.description = "\n".join(lines) if lines else "No users found."
            embed.set_footer(text=f"Total: {len(warns)} users")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="blacklist", aliases=["bl"])
    @commands.has_permissions(moderate_members=True)
    async def blacklist_prefix(self, ctx):
        warns = self.data.load(ctx.guild.id, 'warns')
        embed = discord.Embed(color=Colors.MAIN, title="Server Blacklist")
        if not warns:
            embed.description = "No users with warnings."
        else:
            lines = []
            for user_id, user_warns in list(warns.items())[:15]:
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    lines.append(f"**{user}** - {len(user_warns)} warnings")
                except:
                    lines.append(f"Unknown ({user_id}) - {len(user_warns)} warnings")
            embed.description = "\n".join(lines) if lines else "No users found."
            embed.set_footer(text=f"Total: {len(warns)} users")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # MOD LOGS COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="mod-logs", description="Set moderation logs channel")
    @app_commands.describe(channel="Channel for mod logs")
    @app_commands.default_permissions(administrator=True)
    async def modlogs_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        settings = self.data.load(interaction.guild.id, 'settings')
        settings['log_channel'] = channel.id
        self.data.save(interaction.guild.id, 'settings', settings)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Mod logs channel set to {channel.mention}")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="modlogs", aliases=["setlogs"])
    @commands.has_permissions(administrator=True)
    async def modlogs_prefix(self, ctx, channel: discord.TextChannel):
        settings = self.data.load(ctx.guild.id, 'settings')
        settings['log_channel'] = channel.id
        self.data.save(ctx.guild.id, 'settings', settings)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Mod logs channel set to {channel.mention}")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # CLEAR COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear_slash(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message(f"{Emojis.CROSS} Amount must be 1-100.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"{Emojis.CHECK} Deleted {len(deleted)} messages.", ephemeral=True)

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_prefix(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send(f"{Emojis.CROSS} Amount must be 1-100.")
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"{Emojis.CHECK} Deleted {len(deleted) - 1} messages.")
        await msg.delete(delay=3)

    # ═══════════════════════════════════════════════════════════
    # SLOWMODE COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(seconds="Slowmode in seconds (0 to disable)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode_slash(self, interaction: discord.Interaction, seconds: int):
        if seconds < 0 or seconds > 21600:
            return await interaction.response.send_message(f"{Emojis.CROSS} Slowmode must be 0-21600 seconds.", ephemeral=True)
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Slowmode disabled.")
        else:
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Slowmode set to {seconds} seconds.")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="slowmode", aliases=["sm"])
    @commands.has_permissions(manage_channels=True)
    async def slowmode_prefix(self, ctx, seconds: int):
        if seconds < 0 or seconds > 21600:
            return await ctx.send(f"{Emojis.CROSS} Slowmode must be 0-21600 seconds.")
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Slowmode disabled.")
        else:
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Slowmode set to {seconds} seconds.")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # LOCK / UNLOCK CHANNEL
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="lock", description="Lock a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def lock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Channel locked.")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock_prefix(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Channel locked.")
        await ctx.send(embed=embed)

    @app_commands.command(name="unlock", description="Unlock a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Channel unlocked.")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock_prefix(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Channel unlocked.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))