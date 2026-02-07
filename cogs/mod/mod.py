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

    async def check_mod_action(self, ctx_or_interaction, member, action):
        """Check if mod action can be performed and return error message if not"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        user = ctx_or_interaction.user if is_interaction else ctx_or_interaction.author
        guild = ctx_or_interaction.guild
        
        # Check if member is None
        if member is None:
            return f"{Emojis.CROSS} Please mention a valid member."
        
        # Check if trying to action yourself
        if member.id == user.id:
            return f"{Emojis.CROSS} You cannot {action} yourself."
        
        # Check if trying to action the bot
        if member.id == self.bot.user.id:
            return f"{Emojis.CROSS} I cannot {action} myself."
        
        # Check if trying to action the owner
        if member.id == guild.owner_id:
            return f"{Emojis.CROSS} You cannot {action} the server owner."
        
        # Check role hierarchy (user vs target)
        if member.top_role >= user.top_role and user.id != guild.owner_id:
            return f"{Emojis.CROSS} You cannot {action} **{member}** because their role is equal to or higher than yours."
        
        # Check role hierarchy (bot vs target)
        if member.top_role >= guild.me.top_role:
            return f"{Emojis.CROSS} I cannot {action} **{member}** because their role is equal to or higher than mine."
        
        return None  # No error, action can proceed

    async def send_error(self, ctx_or_interaction, message, ephemeral=True):
        """Send error message to user"""
        embed = discord.Embed(color=Colors.ERROR, description=message)
        if isinstance(ctx_or_interaction, discord.Interaction):
            if ctx_or_interaction.response.is_done():
                await ctx_or_interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await ctx_or_interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            await ctx_or_interaction.send(embed=embed)

    async def send_success(self, ctx_or_interaction, message):
        """Send success message to user"""
        embed = discord.Embed(color=Colors.MAIN, description=message)
        user = ctx_or_interaction.user if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author
        embed.set_footer(text=f"By {user}", icon_url=user.display_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            if ctx_or_interaction.response.is_done():
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # KICK COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        error = await self.check_mod_action(interaction, member, "kick")
        if error:
            return await self.send_error(interaction, error)
        
        try:
            await member.send(f"You have been kicked from **{interaction.guild.name}**\n**Reason:** {reason}")
        except:
            pass
        
        await member.kick(reason=f"{reason} | By: {interaction.user}")
        await self.send_success(interaction, f"{Emojis.CHECK} **{member}** has been kicked.\n**Reason:** {reason}")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_prefix(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to kick.\n**Usage:** `!kick @member [reason]`")
        
        error = await self.check_mod_action(ctx, member, "kick")
        if error:
            return await self.send_error(ctx, error)
        
        try:
            await member.send(f"You have been kicked from **{ctx.guild.name}**\n**Reason:** {reason}")
        except:
            pass
        
        await member.kick(reason=f"{reason} | By: {ctx.author}")
        await self.send_success(ctx, f"{Emojis.CHECK} **{member}** has been kicked.\n**Reason:** {reason}")

    @kick_prefix.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to kick.\n**Usage:** `!kick @member [reason]`")
        elif isinstance(error, commands.MemberNotFound):
            await self.send_error(ctx, f"{Emojis.CROSS} Member not found. Please mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await self.send_error(ctx, f"{Emojis.CROSS} You don't have permission to kick members.")
        elif isinstance(error, commands.BotMissingPermissions):
            await self.send_error(ctx, f"{Emojis.CROSS} I don't have permission to kick members.")

    # ═══════════════════════════════════════════════════════════
    # BAN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        error = await self.check_mod_action(interaction, member, "ban")
        if error:
            return await self.send_error(interaction, error)
        
        try:
            await member.send(f"You have been banned from **{interaction.guild.name}**\n**Reason:** {reason}")
        except:
            pass
        
        await member.ban(reason=f"{reason} | By: {interaction.user}")
        await self.send_success(interaction, f"{Emojis.CHECK} **{member}** has been banned.\n**Reason:** {reason}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to ban.\n**Usage:** `!ban @member [reason]`")
        
        error = await self.check_mod_action(ctx, member, "ban")
        if error:
            return await self.send_error(ctx, error)
        
        try:
            await member.send(f"You have been banned from **{ctx.guild.name}**\n**Reason:** {reason}")
        except:
            pass
        
        await member.ban(reason=f"{reason} | By: {ctx.author}")
        await self.send_success(ctx, f"{Emojis.CHECK} **{member}** has been banned.\n**Reason:** {reason}")

    @ban_prefix.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to ban.\n**Usage:** `!ban @member [reason]`")
        elif isinstance(error, commands.MemberNotFound):
            await self.send_error(ctx, f"{Emojis.CROSS} Member not found. Please mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await self.send_error(ctx, f"{Emojis.CROSS} You don't have permission to ban members.")
        elif isinstance(error, commands.BotMissingPermissions):
            await self.send_error(ctx, f"{Emojis.CROSS} I don't have permission to ban members.")

    # ═══════════════════════════════════════════════════════════
    # UNBAN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(user_id="User ID to unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, user_id: str):
        try:
            user_id_int = int(user_id)
        except ValueError:
            return await self.send_error(interaction, f"{Emojis.CROSS} Invalid user ID. Please provide a valid number.")
        
        try:
            user = await self.bot.fetch_user(user_id_int)
            await interaction.guild.unban(user)
            await self.send_success(interaction, f"{Emojis.CHECK} **{user}** has been unbanned.")
        except discord.NotFound:
            await self.send_error(interaction, f"{Emojis.CROSS} User not found or not banned.")
        except Exception as e:
            await self.send_error(interaction, f"{Emojis.CROSS} Failed to unban: {str(e)}")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_prefix(self, ctx, user_id: str = None):
        if user_id is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please provide a user ID to unban.\n**Usage:** `!unban <user_id>`")
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            return await self.send_error(ctx, f"{Emojis.CROSS} Invalid user ID. Please provide a valid number.")
        
        try:
            user = await self.bot.fetch_user(user_id_int)
            await ctx.guild.unban(user)
            await self.send_success(ctx, f"{Emojis.CHECK} **{user}** has been unbanned.")
        except discord.NotFound:
            await self.send_error(ctx, f"{Emojis.CROSS} User not found or not banned.")
        except Exception as e:
            await self.send_error(ctx, f"{Emojis.CROSS} Failed to unban: {str(e)}")

    # ═══════════════════════════════════════════════════════════
    # TIMEOUT COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member to timeout", duration="Duration (e.g., 30s, 5m, 1h, 1d)", reason="Reason")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        error = await self.check_mod_action(interaction, member, "timeout")
        if error:
            return await self.send_error(interaction, error)
        
        seconds = self.parse_duration(duration)
        if not seconds:
            return await self.send_error(interaction, f"{Emojis.CROSS} Invalid duration format.\n**Examples:** `30s`, `5m`, `1h`, `1d`")
        
        if seconds > 2419200:  # 28 days max
            return await self.send_error(interaction, f"{Emojis.CROSS} Timeout cannot exceed 28 days.")
        
        try:
            await member.send(f"You have been timed out in **{interaction.guild.name}** for **{duration}**\n**Reason:** {reason}")
        except:
            pass
        
        await member.timeout(timedelta(seconds=seconds), reason=f"{reason} | By: {interaction.user}")
        await self.send_success(interaction, f"{Emojis.CHECK} **{member}** has been timed out for **{duration}**.\n**Reason:** {reason}")

    @commands.command(name="timeout", aliases=["mute", "to"])
    @commands.has_permissions(moderate_members=True)
    async def timeout_prefix(self, ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to timeout.\n**Usage:** `!timeout @member <duration> [reason]`\n**Examples:** `!timeout @user 5m Spamming`")
        
        if duration is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please provide a duration.\n**Examples:** `30s`, `5m`, `1h`, `1d`")
        
        error = await self.check_mod_action(ctx, member, "timeout")
        if error:
            return await self.send_error(ctx, error)
        
        seconds = self.parse_duration(duration)
        if not seconds:
            return await self.send_error(ctx, f"{Emojis.CROSS} Invalid duration format.\n**Examples:** `30s`, `5m`, `1h`, `1d`")
        
        if seconds > 2419200:
            return await self.send_error(ctx, f"{Emojis.CROSS} Timeout cannot exceed 28 days.")
        
        try:
            await member.send(f"You have been timed out in **{ctx.guild.name}** for **{duration}**\n**Reason:** {reason}")
        except:
            pass
        
        await member.timeout(timedelta(seconds=seconds), reason=f"{reason} | By: {ctx.author}")
        await self.send_success(ctx, f"{Emojis.CHECK} **{member}** has been timed out for **{duration}**.\n**Reason:** {reason}")

    @timeout_prefix.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_error(ctx, f"{Emojis.CROSS} Missing arguments.\n**Usage:** `!timeout @member <duration> [reason]`\n**Example:** `!timeout @user 5m Spamming`")
        elif isinstance(error, commands.MemberNotFound):
            await self.send_error(ctx, f"{Emojis.CROSS} Member not found. Please mention a valid member.")
        elif isinstance(error, commands.MissingPermissions):
            await self.send_error(ctx, f"{Emojis.CROSS} You don't have permission to timeout members.")

    # ═══════════════════════════════════════════════════════════
    # REMOVE TIMEOUT COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="remove-timeout", description="Remove timeout from a member")
    @app_commands.describe(member="Member to untimeout")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout_slash(self, interaction: discord.Interaction, member: discord.Member):
        if not member.is_timed_out():
            return await self.send_error(interaction, f"{Emojis.CROSS} **{member}** is not currently timed out.")
        
        await member.timeout(None)
        await self.send_success(interaction, f"{Emojis.CHECK} Timeout removed from **{member}**.")

    @commands.command(name="untimeout", aliases=["unmute", "removetimeout"])
    @commands.has_permissions(moderate_members=True)
    async def untimeout_prefix(self, ctx, member: discord.Member = None):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to untimeout.\n**Usage:** `!untimeout @member`")
        
        if not member.is_timed_out():
            return await self.send_error(ctx, f"{Emojis.CROSS} **{member}** is not currently timed out.")
        
        await member.timeout(None)
        await self.send_success(ctx, f"{Emojis.CHECK} Timeout removed from **{member}**.")

    # ═══════════════════════════════════════════════════════════
    # WARN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for warning")
    @app_commands.default_permissions(moderate_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        error = await self.check_mod_action(interaction, member, "warn")
        if error:
            return await self.send_error(interaction, error)
        
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
        
        try:
            await member.send(f"You have been warned in **{interaction.guild.name}**\n**Reason:** {reason}\n**Total Warnings:** {len(user_warns)}")
        except:
            pass
        
        await self.send_success(interaction, f"{Emojis.CHECK} **{member}** has been warned.\n**Reason:** {reason}\n**Total Warnings:** {len(user_warns)}")

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn_prefix(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member to warn.\n**Usage:** `!warn @member [reason]`")
        
        error = await self.check_mod_action(ctx, member, "warn")
        if error:
            return await self.send_error(ctx, error)
        
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
        
        try:
            await member.send(f"You have been warned in **{ctx.guild.name}**\n**Reason:** {reason}\n**Total Warnings:** {len(user_warns)}")
        except:
            pass
        
        await self.send_success(ctx, f"{Emojis.CHECK} **{member}** has been warned.\n**Reason:** {reason}\n**Total Warnings:** {len(user_warns)}")

    # ═══════════════════════════════════════════════════════════
    # REMOVE WARN COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="remove-warn", description="Remove a warning from a member")
    @app_commands.describe(member="Member", warn_id="Warning ID to remove")
    @app_commands.default_permissions(moderate_members=True)
    async def removewarn_slash(self, interaction: discord.Interaction, member: discord.Member, warn_id: int):
        warns = self.data.load(interaction.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        
        if not user_warns:
            return await self.send_error(interaction, f"{Emojis.CROSS} **{member}** has no warnings.")
        
        new_warns = [w for w in user_warns if w['id'] != warn_id]
        if len(new_warns) == len(user_warns):
            return await self.send_error(interaction, f"{Emojis.CROSS} Warning **#{warn_id}** not found for **{member}**.")
        
        warns[str(member.id)] = new_warns
        self.data.save(interaction.guild.id, 'warns', warns)
        await self.send_success(interaction, f"{Emojis.CHECK} Warning **#{warn_id}** removed from **{member}**.\n**Remaining Warnings:** {len(new_warns)}")

    @commands.command(name="removewarn", aliases=["delwarn", "unwarn"])
    @commands.has_permissions(moderate_members=True)
    async def removewarn_prefix(self, ctx, member: discord.Member = None, warn_id: int = None):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member.\n**Usage:** `!removewarn @member <warn_id>`")
        
        if warn_id is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please provide a warning ID.\n**Usage:** `!removewarn @member <warn_id>`\nUse `!warnings @member` to see warning IDs.")
        
        warns = self.data.load(ctx.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        
        if not user_warns:
            return await self.send_error(ctx, f"{Emojis.CROSS} **{member}** has no warnings.")
        
        new_warns = [w for w in user_warns if w['id'] != warn_id]
        if len(new_warns) == len(user_warns):
            return await self.send_error(ctx, f"{Emojis.CROSS} Warning **#{warn_id}** not found for **{member}**.")
        
        warns[str(member.id)] = new_warns
        self.data.save(ctx.guild.id, 'warns', warns)
        await self.send_success(ctx, f"{Emojis.CHECK} Warning **#{warn_id}** removed from **{member}**.\n**Remaining Warnings:** {len(new_warns)}")

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
            embed.description = f"{Emojis.CHECK} This member has no warnings."
        else:
            lines = []
            for w in user_warns[-10:]:
                mod = interaction.guild.get_member(w['mod'])
                mod_name = mod.name if mod else "Unknown"
                lines.append(f"**#{w['id']}** - {w['reason'][:50]}\n> By: {mod_name}")
            embed.description = "\n\n".join(lines)
            embed.set_footer(text=f"Total: {len(user_warns)} warning(s)")
        
        await interaction.response.send_message(embed=embed)

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings_prefix(self, ctx, member: discord.Member = None):
        if member is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a member.\n**Usage:** `!warnings @member`")
        
        warns = self.data.load(ctx.guild.id, 'warns')
        user_warns = warns.get(str(member.id), [])
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name=f"Warnings for {member}", icon_url=member.display_avatar.url)
        
        if not user_warns:
            embed.description = f"{Emojis.CHECK} This member has no warnings."
        else:
            lines = []
            for w in user_warns[-10:]:
                mod = ctx.guild.get_member(w['mod'])
                mod_name = mod.name if mod else "Unknown"
                lines.append(f"**#{w['id']}** - {w['reason'][:50]}\n> By: {mod_name}")
            embed.description = "\n\n".join(lines)
            embed.set_footer(text=f"Total: {len(user_warns)} warning(s)")
        
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # BLACKLIST COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="blacklist", description="View all users with warnings")
    @app_commands.default_permissions(moderate_members=True)
    async def blacklist_slash(self, interaction: discord.Interaction):
        warns = self.data.load(interaction.guild.id, 'warns')
        
        embed = discord.Embed(color=Colors.MAIN, title=f"{Emojis.CROSS} Server Blacklist")
        
        if not warns:
            embed.description = "No users with warnings."
        else:
            lines = []
            for user_id, user_warns in list(warns.items())[:15]:
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    lines.append(f"**{user}** - {len(user_warns)} warning(s)")
                except:
                    lines.append(f"Unknown User ({user_id}) - {len(user_warns)} warning(s)")
            embed.description = "\n".join(lines)
            embed.set_footer(text=f"Total: {len(warns)} user(s) with warnings")
        
        await interaction.response.send_message(embed=embed)

    @commands.command(name="blacklist", aliases=["bl"])
    @commands.has_permissions(moderate_members=True)
    async def blacklist_prefix(self, ctx):
        warns = self.data.load(ctx.guild.id, 'warns')
        
        embed = discord.Embed(color=Colors.MAIN, title=f"{Emojis.CROSS} Server Blacklist")
        
        if not warns:
            embed.description = "No users with warnings."
        else:
            lines = []
            for user_id, user_warns in list(warns.items())[:15]:
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    lines.append(f"**{user}** - {len(user_warns)} warning(s)")
                except:
                    lines.append(f"Unknown User ({user_id}) - {len(user_warns)} warning(s)")
            embed.description = "\n".join(lines)
            embed.set_footer(text=f"Total: {len(warns)} user(s) with warnings")
        
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
        await self.send_success(interaction, f"{Emojis.CHECK} Mod logs channel set to {channel.mention}")

    @commands.command(name="modlogs", aliases=["setlogs"])
    @commands.has_permissions(administrator=True)
    async def modlogs_prefix(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please mention a channel.\n**Usage:** `!modlogs #channel`")
        
        settings = self.data.load(ctx.guild.id, 'settings')
        settings['log_channel'] = channel.id
        self.data.save(ctx.guild.id, 'settings', settings)
        await self.send_success(ctx, f"{Emojis.CHECK} Mod logs channel set to {channel.mention}")

    # ═══════════════════════════════════════════════════════════
    # CLEAR COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear_slash(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await self.send_error(interaction, f"{Emojis.CROSS} Amount must be between 1 and 100.")
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"{Emojis.CHECK} Successfully deleted **{len(deleted)}** messages.", ephemeral=True)

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_prefix(self, ctx, amount: int = None):
        if amount is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please provide an amount.\n**Usage:** `!clear <1-100>`")
        
        if amount < 1 or amount > 100:
            return await self.send_error(ctx, f"{Emojis.CROSS} Amount must be between 1 and 100.")
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"{Emojis.CHECK} Successfully deleted **{len(deleted) - 1}** messages.")
        await msg.delete(delay=3)

    # ═══════════════════════════════════════════════════════════
    # SLOWMODE COMMAND
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(seconds="Slowmode in seconds (0 to disable)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode_slash(self, interaction: discord.Interaction, seconds: int):
        if seconds < 0 or seconds > 21600:
            return await self.send_error(interaction, f"{Emojis.CROSS} Slowmode must be between 0 and 21600 seconds (6 hours).")
        
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await self.send_success(interaction, f"{Emojis.CHECK} Slowmode has been disabled.")
        else:
            await self.send_success(interaction, f"{Emojis.CHECK} Slowmode set to **{seconds}** seconds.")

    @commands.command(name="slowmode", aliases=["sm"])
    @commands.has_permissions(manage_channels=True)
    async def slowmode_prefix(self, ctx, seconds: int = None):
        if seconds is None:
            return await self.send_error(ctx, f"{Emojis.CROSS} Please provide seconds.\n**Usage:** `!slowmode <0-21600>`\nUse 0 to disable.")
        
        if seconds < 0 or seconds > 21600:
            return await self.send_error(ctx, f"{Emojis.CROSS} Slowmode must be between 0 and 21600 seconds (6 hours).")
        
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await self.send_success(ctx, f"{Emojis.CHECK} Slowmode has been disabled.")
        else:
            await self.send_success(ctx, f"{Emojis.CHECK} Slowmode set to **{seconds}** seconds.")

    # ═══════════════════════════════════════════════════════════
    # LOCK / UNLOCK CHANNEL
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="lock", description="Lock a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def lock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await self.send_success(interaction, f"{Emojis.CHECK} This channel has been locked. Only staff can send messages.")

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock_prefix(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await self.send_success(ctx, f"{Emojis.CHECK} This channel has been locked. Only staff can send messages.")

    @app_commands.command(name="unlock", description="Unlock a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock_slash(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await self.send_success(interaction, f"{Emojis.CHECK} This channel has been unlocked. Everyone can send messages.")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock_prefix(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await self.send_success(ctx, f"{Emojis.CHECK} This channel has been unlocked. Everyone can send messages.")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))