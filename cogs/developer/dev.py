import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone
import json
import os
import aiohttp

from config import Colors, Emojis

# Your Developer ID - CHANGE THIS TO YOUR ID
DEVELOPER_ID = 1464984679982567454


class StatusType:
    WATCHING = "watching"
    LISTENING = "listening"
    PLAYING = "playing"
    STREAMING = "streaming"


class StatusValue:
    USER_COUNT = "user-count"
    SERVER_COUNT = "server-count"
    COMMANDS_COUNT = "commands-count"
    UPTIME = "uptime"
    CUSTOM = "custom"


def is_developer():
    """Check if user is the developer"""
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == DEVELOPER_ID
    return app_commands.check(predicate)


def is_developer_prefix():
    """Check if user is the developer (prefix commands)"""
    async def predicate(ctx):
        return ctx.author.id == DEVELOPER_ID
    return commands.check(predicate)


class DeveloperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/status.json'
        self.status_config = self.load_status()
        self.update_status.start()

    def cog_unload(self):
        self.update_status.cancel()

    def load_status(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"type": "watching", "value": "server-count", "custom": "", "stream_url": ""}

    def save_status(self):
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.status_config, f, indent=4)

    def get_status_text(self):
        value = self.status_config.get("value", "server-count")
        
        if value == "user-count":
            return f"{len(set(self.bot.get_all_members())):,} users"
        elif value == "server-count":
            return f"{len(self.bot.guilds):,} servers"
        elif value == "commands-count":
            return f"{len(self.bot.commands) + len(self.bot.tree.get_commands())} commands"
        elif value == "uptime":
            delta = datetime.now(timezone.utc) - self.bot.start_time
            hours, rem = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(rem, 60)
            return f"{hours}h {minutes}m uptime"
        else:
            return self.status_config.get("custom", "Premium Bot")

    def get_activity(self):
        status_type = self.status_config.get("type", "watching")
        text = self.get_status_text()
        
        if status_type == "watching":
            return discord.Activity(type=discord.ActivityType.watching, name=text)
        elif status_type == "listening":
            return discord.Activity(type=discord.ActivityType.listening, name=text)
        elif status_type == "playing":
            return discord.Game(name=text)
        elif status_type == "streaming":
            url = self.status_config.get("stream_url", "https://twitch.tv/discord")
            return discord.Streaming(name=text, url=url)
        
        return discord.Activity(type=discord.ActivityType.watching, name=text)

    @tasks.loop(seconds=30)
    async def update_status(self):
        """Auto-update status every 30 seconds"""
        if self.bot.is_ready():
            try:
                activity = self.get_activity()
                await self.bot.change_presence(activity=activity)
            except:
                pass

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()

    # ═══════════════════════════════════════════════════════════════
    #  SETUP-STATUS COMMAND
    # ═══════════════════════════════════════════════════════════════
    
    @app_commands.command(name="setup-status", description="🔒 Set bot status (Developer only)")
    @app_commands.describe(
        status_type="Status type",
        value="What to display",
        custom_text="Custom text (if value is custom)",
        stream_url="Twitch/YouTube URL (if streaming)"
    )
    @app_commands.choices(status_type=[
        app_commands.Choice(name="👀 Watching", value="watching"),
        app_commands.Choice(name="🎧 Listening", value="listening"),
        app_commands.Choice(name="🎮 Playing", value="playing"),
        app_commands.Choice(name="📺 Streaming", value="streaming"),
    ])
    @app_commands.choices(value=[
        app_commands.Choice(name="👥 User Count", value="user-count"),
        app_commands.Choice(name="🖥️ Server Count", value="server-count"),
        app_commands.Choice(name="⚡ Commands Count", value="commands-count"),
        app_commands.Choice(name="⏱️ Uptime", value="uptime"),
        app_commands.Choice(name="✏️ Custom Message", value="custom"),
    ])
    @is_developer()
    async def setup_status_slash(
        self, 
        interaction: discord.Interaction, 
        status_type: str,
        value: str,
        custom_text: str = None,
        stream_url: str = None
    ):
        self.status_config["type"] = status_type
        self.status_config["value"] = value
        
        if custom_text:
            self.status_config["custom"] = custom_text
        if stream_url:
            self.status_config["stream_url"] = stream_url
        
        self.save_status()
        
        # Update immediately
        activity = self.get_activity()
        await self.bot.change_presence(activity=activity)
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Status Updated", icon_url=self.bot.user.display_avatar.url)
        
        type_emoji = {"watching": "👀", "listening": "🎧", "playing": "🎮", "streaming": "📺"}
        value_emoji = {"user-count": "👥", "server-count": "🖥️", "commands-count": "⚡", "uptime": "⏱️", "custom": "✏️"}
        
        embed.add_field(name="Type", value=f"{type_emoji.get(status_type, '📊')} {status_type.title()}", inline=True)
        embed.add_field(name="Value", value=f"{value_emoji.get(value, '📊')} {value.replace('-', ' ').title()}", inline=True)
        embed.add_field(name="Current", value=f"`{self.get_status_text()}`", inline=True)
        
        if value == "custom" and custom_text:
            embed.add_field(name="Custom Text", value=custom_text, inline=False)
        if status_type == "streaming" and stream_url:
            embed.add_field(name="Stream URL", value=stream_url, inline=False)
        
        embed.set_footer(text="Status will auto-update every 30 seconds")
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ═══════════════════════════════════════════════════════════════
    #  CHANGE-PROFILE COMMAND
    # ═══════════════════════════════════════════════════════════════
    
    @app_commands.command(name="change-profile", description="🔒 Change bot avatar (Developer only)")
    @app_commands.describe(image="New avatar image")
    @is_developer()
    async def change_profile_slash(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(ephemeral=True)
        
        if not image.content_type or not image.content_type.startswith('image/'):
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Please upload an image file.")
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            image_bytes = await image.read()
            await self.bot.user.edit(avatar=image_bytes)
            
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Avatar Updated", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"{Emojis.CHECK} Bot avatar has been changed!"
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.timestamp = datetime.now(timezone.utc)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.HTTPException as e:
            embed = discord.Embed(color=Colors.ERROR)
            embed.description = f"{Emojis.CROSS} Failed to change avatar: {str(e)}"
            await interaction.followup.send(embed=embed, ephemeral=True)

    # ═══════════════════════════════════════════════════════════════
    #  CHANGE-BANNER COMMAND
    # ═══════════════════════════════════════════════════════════════
    
    @app_commands.command(name="change-banner", description="🔒 Change bot banner (Developer only)")
    @app_commands.describe(image="New banner image")
    @is_developer()
    async def change_banner_slash(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(ephemeral=True)
        
        if not image.content_type or not image.content_type.startswith('image/'):
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Please upload an image file.")
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            image_bytes = await image.read()
            await self.bot.user.edit(banner=image_bytes)
            
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Banner Updated", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"{Emojis.CHECK} Bot banner has been changed!"
            embed.timestamp = datetime.now(timezone.utc)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.HTTPException as e:
            embed = discord.Embed(color=Colors.ERROR)
            if "premium" in str(e).lower() or "nitro" in str(e).lower():
                embed.description = f"{Emojis.CROSS} Bot needs Nitro to have a banner."
            else:
                embed.description = f"{Emojis.CROSS} Failed to change banner: {str(e)}"
            await interaction.followup.send(embed=embed, ephemeral=True)

    # ═══════════════════════════════════════════════════════════════
    #  SHUTDOWN COMMAND
    # ═══════════════════════════════════════════════════════════════
    
    @app_commands.command(name="shutdown", description="🔒 Shutdown the bot (Developer only)")
    @is_developer()
    async def shutdown_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Shutting Down", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Bot is shutting down... Goodbye! 👋"
        embed.timestamp = datetime.now(timezone.utc)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.bot.close()

    # ═══════════════════════════════════════════════════════════════
    #  PREFIX COMMANDS (HIDDEN)
    # ═══════════════════════════════════════════════════════════════
    
    @commands.command(name="setup-status", hidden=True)
    @is_developer_prefix()
    async def setup_status_prefix(self, ctx, status_type: str = None, value: str = None, *, custom: str = None):
        if not status_type or not value:
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Setup Status", icon_url=self.bot.user.display_avatar.url)
            embed.description = "Set the bot's status"
            embed.add_field(
                name="Usage",
                value=f"`{ctx.prefix}setup-status <type> <value> [custom]`",
                inline=False
            )
            embed.add_field(
                name="Types",
                value="`watching`, `listening`, `playing`, `streaming`",
                inline=True
            )
            embed.add_field(
                name="Values",
                value="`user-count`, `server-count`, `commands-count`, `uptime`, `custom`",
                inline=True
            )
            embed.add_field(
                name="Example",
                value=f"`{ctx.prefix}setup-status watching server-count`\n`{ctx.prefix}setup-status playing custom My Custom Status`",
                inline=False
            )
            return await ctx.send(embed=embed)
        
        valid_types = ["watching", "listening", "playing", "streaming"]
        valid_values = ["user-count", "server-count", "commands-count", "uptime", "custom"]
        
        if status_type.lower() not in valid_types:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Invalid type. Use: {', '.join(valid_types)}")
            return await ctx.send(embed=embed)
        
        if value.lower() not in valid_values:
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Invalid value. Use: {', '.join(valid_values)}")
            return await ctx.send(embed=embed)
        
        self.status_config["type"] = status_type.lower()
        self.status_config["value"] = value.lower()
        
        if custom and value.lower() == "custom":
            self.status_config["custom"] = custom
        
        self.save_status()
        
        activity = self.get_activity()
        await self.bot.change_presence(activity=activity)
        
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Status Updated", icon_url=self.bot.user.display_avatar.url)
        embed.add_field(name="Type", value=status_type.title(), inline=True)
        embed.add_field(name="Value", value=value.replace('-', ' ').title(), inline=True)
        embed.add_field(name="Current", value=f"`{self.get_status_text()}`", inline=True)
        embed.set_footer(text="Status will auto-update every 30 seconds")
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)

    @commands.command(name="change-profile", aliases=["setavatar"], hidden=True)
    @is_developer_prefix()
    async def change_profile_prefix(self, ctx):
        if not ctx.message.attachments:
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Change Profile", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"Attach an image to change the bot's avatar.\n\n**Usage:** `{ctx.prefix}change-profile` (with image attached)"
            return await ctx.send(embed=embed)
        
        image = ctx.message.attachments[0]
        
        if not image.content_type or not image.content_type.startswith('image/'):
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Please attach an image file.")
            return await ctx.send(embed=embed)
        
        try:
            image_bytes = await image.read()
            await self.bot.user.edit(avatar=image_bytes)
            
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Avatar Updated", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"{Emojis.CHECK} Bot avatar has been changed!"
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.timestamp = datetime.now(timezone.utc)
            
            await ctx.send(embed=embed)
        except discord.HTTPException as e:
            embed = discord.Embed(color=Colors.ERROR)
            embed.description = f"{Emojis.CROSS} Failed to change avatar: {str(e)}"
            await ctx.send(embed=embed)

    @commands.command(name="change-banner", aliases=["setbanner"], hidden=True)
    @is_developer_prefix()
    async def change_banner_prefix(self, ctx):
        if not ctx.message.attachments:
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Change Banner", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"Attach an image to change the bot's banner.\n\n**Usage:** `{ctx.prefix}change-banner` (with image attached)"
            return await ctx.send(embed=embed)
        
        image = ctx.message.attachments[0]
        
        if not image.content_type or not image.content_type.startswith('image/'):
            embed = discord.Embed(color=Colors.ERROR, description=f"{Emojis.CROSS} Please attach an image file.")
            return await ctx.send(embed=embed)
        
        try:
            image_bytes = await image.read()
            await self.bot.user.edit(banner=image_bytes)
            
            embed = discord.Embed(color=Colors.MAIN)
            embed.set_author(name="Banner Updated", icon_url=self.bot.user.display_avatar.url)
            embed.description = f"{Emojis.CHECK} Bot banner has been changed!"
            embed.timestamp = datetime.now(timezone.utc)
            
            await ctx.send(embed=embed)
        except discord.HTTPException as e:
            embed = discord.Embed(color=Colors.ERROR)
            if "premium" in str(e).lower():
                embed.description = f"{Emojis.CROSS} Bot needs Nitro to have a banner."
            else:
                embed.description = f"{Emojis.CROSS} Failed to change banner: {str(e)}"
            await ctx.send(embed=embed)

    @commands.command(name="shutdown", aliases=["die", "stop"], hidden=True)
    @is_developer_prefix()
    async def shutdown_prefix(self, ctx):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Shutting Down", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"{Emojis.CHECK} Bot is shutting down... Goodbye! 👋"
        embed.timestamp = datetime.now(timezone.utc)
        
        await ctx.send(embed=embed)
        await self.bot.close()

    # ═══════════════════════════════════════════════════════════════
    #  ERROR HANDLERS
    # ═══════════════════════════════════════════════════════════════
    
    @setup_status_slash.error
    @change_profile_slash.error
    @change_banner_slash.error
    @shutdown_slash.error
    async def dev_slash_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            # Silently ignore - command is hidden from non-developers
            return
        raise error

    @setup_status_prefix.error
    @change_profile_prefix.error
    @change_banner_prefix.error
    @shutdown_prefix.error
    async def dev_prefix_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            # Silently ignore - command is hidden from non-developers
            return
        raise error


async def setup(bot):
    await bot.add_cog(DeveloperCog(bot))