import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone
import json
import os
from config import Colors, Emojis

DEVELOPER_ID = 1464984679982567454

def is_developer():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == DEVELOPER_ID
    return app_commands.check(predicate)

def is_developer_prefix():
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
            return {"type": "watching", "value": "server-count", "custom": ""}

    def save_status(self):
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.status_config, f, indent=4)

    def get_status_text(self):
        value = self.status_config.get("value", "server-count")
        if value == "user-count": return f"{len(set(self.bot.get_all_members())):,} users"
        elif value == "server-count": return f"{len(self.bot.guilds):,} servers"
        elif value == "commands-count": return f"{len(self.bot.commands)} commands"
        elif value == "uptime":
            delta = datetime.now(timezone.utc) - self.bot.start_time
            hours, rem = divmod(int(delta.total_seconds()), 3600)
            minutes, _ = divmod(rem, 60)
            return f"{hours}h {minutes}m uptime"
        else: return self.status_config.get("custom", "Premium Bot")

    def get_activity(self):
        status_type = self.status_config.get("type", "watching")
        text = self.get_status_text()
        if status_type == "watching": return discord.Activity(type=discord.ActivityType.watching, name=text)
        elif status_type == "listening": return discord.Activity(type=discord.ActivityType.listening, name=text)
        elif status_type == "playing": return discord.Game(name=text)
        elif status_type == "streaming": return discord.Streaming(name=text, url=self.status_config.get("stream_url", "https://twitch.tv/discord"))
        return discord.Activity(type=discord.ActivityType.watching, name=text)

    @tasks.loop(seconds=30)
    async def update_status(self):
        if self.bot.is_ready():
            try: await self.bot.change_presence(activity=self.get_activity())
            except: pass

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="setup-status", description="🔒 Set bot status (Developer only)")
    @app_commands.describe(status_type="Status type", value="What to display", custom_text="Custom text", stream_url="Stream URL")
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
    async def setup_status_slash(self, interaction: discord.Interaction, status_type: str, value: str, custom_text: str = None, stream_url: str = None):
        self.status_config["type"] = status_type
        self.status_config["value"] = value
        if custom_text: self.status_config["custom"] = custom_text
        if stream_url: self.status_config["stream_url"] = stream_url
        self.save_status()
        await self.bot.change_presence(activity=self.get_activity())
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Status updated to: **{status_type.title()}** - {self.get_status_text()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="change-profile", description="🔒 Change bot avatar (Developer only)")
    @app_commands.describe(image="New avatar image")
    @is_developer()
    async def change_profile_slash(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(ephemeral=True)
        try:
            image_bytes = await image.read()
            await self.bot.user.edit(avatar=image_bytes)
            embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Avatar updated!")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}", ephemeral=True)

    @app_commands.command(name="shutdown", description="🔒 Shutdown bot (Developer only)")
    @is_developer()
    async def shutdown_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(color=Colors.MAIN, description=f"{Emojis.CHECK} Shutting down... Goodbye! 👋")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.bot.close()

    @setup_status_slash.error
    @change_profile_slash.error
    @shutdown_slash.error
    async def dev_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure): return
        raise error

async def setup(bot):
    await bot.add_cog(DeveloperCog(bot))