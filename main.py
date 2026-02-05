import discord
from discord.ext import commands
import os
import asyncio
from datetime import datetime, timezone
import traceback
import logging
from keep_alive import keep_alive

# ═══════════════════════════════════════════════════════════════
#  🎨 PREMIUM BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Set up premium logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('discord')

# Bot configuration
BOT_CONFIG = {
    'prefix': '!',                    # Command prefix
    'developer': '<@1464984679982567454>',
    'version': '1.0.0',
    'color': 0x5865F2,
    'support_server': 'https://discord.gg/NJZvYZP4Cd',
    'github': None
}

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# ═══════════════════════════════════════════════════════════════
#  🤖 PREMIUM BOT CLASS
# ═══════════════════════════════════════════════════════════════

class PremiumBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(BOT_CONFIG['prefix']),
            intents=intents,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True
        )
        # Bot metadata
        self.start_time = datetime.now(timezone.utc)
        self.developer = BOT_CONFIG['developer']
        self.version = BOT_CONFIG['version']
        self.default_color = BOT_CONFIG['color']
        self.support_server = BOT_CONFIG['support_server']
        self.github = BOT_CONFIG['github']

        # Statistics
        self.commands_used = 0
        self.errors_caught = 0

    async def setup_hook(self):
        """Load all cogs and sync commands"""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           🚀 PREMIUM BOT - INITIALIZATION                    ║")
        print("╠══════════════════════════════════════════════════════════════╣")

        # Define cogs to load
        cog_files = [
            'cogs.info.ping',
            'cogs.info.uptime',
            'cogs.info.info'
        ]

        loaded = 0
        failed = 0

        for cog in cog_files:
            try:
                await self.load_extension(cog)
                print(f"║  ✅ Loaded: {cog:<48} ║")
                loaded += 1
            except Exception as e:
                print(f"║  ❌ Failed: {cog:<48} ║")
                print(f"║     Error: {str(e)[:45]:<48} ║")
                failed += 1
                traceback.print_exc()

        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  📊 Loaded: {loaded} | Failed: {failed} | Total: {len(cog_files):<24} ║")
        print("╚══════════════════════════════════════════════════════════════╝")

        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"\n🔄 Synced {len(synced)} slash command(s) globally")
        except Exception as e:
            print(f"\n❌ Failed to sync commands: {e}")

bot = PremiumBot()

# ═══════════════════════════════════════════════════════════════
#  📡 EVENT HANDLERS
# ═══════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    """Called when bot is ready"""
    print()
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃                    🌟 BOT IS NOW ONLINE 🌟                    ┃")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    print(f"┃  🤖 Bot Name    : {bot.user.name:<42} ┃")
    print(f"┃  🆔 Bot ID      : {bot.user.id:<42} ┃")
    print(f"┃  📊 Servers     : {len(bot.guilds):<42} ┃")
    print(f"┃  👥 Users       : {len(set(bot.get_all_members())):<42} ┃")
    print(f"┃  🎯 Commands    : {len([c for c in bot.walk_commands()]):<42} ┃")
    print(f"┃  📌 Prefix      : {BOT_CONFIG['prefix']:<42} ┃")
    print(f"┃  🔖 Version     : {bot.version:<42} ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print()

    # Set premium status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"✨ /help | {len(bot.guilds)} servers"
        ),
        status=discord.Status.online
    )

@bot.event
async def on_guild_join(guild):
    """Called when bot joins a server"""
    print(f"📥 Joined server: {guild.name} (ID: {guild.id}) | Members: {guild.member_count}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"✨ /help | {len(bot.guilds)} servers"
        )
    )

@bot.event
async def on_guild_remove(guild):
    """Called when bot leaves a server"""
    print(f"📤 Left server: {guild.name} (ID: {guild.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"✨ /help | {len(bot.guilds)} servers"
        )
    )

@bot.event
async def on_command(ctx):
    """Track command usage"""
    bot.commands_used += 1

# ═══════════════════════════════════════════════════════════════
#  ⚠️ ERROR HANDLING
# ═══════════════════════════════════════════════════════════════

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for prefix commands"""
    bot.errors_caught += 1

    # Create error embed
    embed = discord.Embed(color=0xFF4444)

    if isinstance(error, commands.CommandNotFound):
        embed.title = "❌ Command Not Found"
        embed.description = f"Use `{BOT_CONFIG['prefix']}help` or `/help` to see available commands."
    elif isinstance(error, commands.MissingPermissions):
        embed.title = "🔒 Missing Permissions"
        embed.description = "You don't have permission to use this command."
        embed.add_field(name="Required", value=", ".join(error.missing_permissions))
    elif isinstance(error, commands.BotMissingPermissions):
        embed.title = "🤖 Bot Missing Permissions"
        embed.description = "I don't have the required permissions."
        embed.add_field(name="Required", value=", ".join(error.missing_permissions))
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.title = "📝 Missing Argument"
        embed.description = f"Missing required argument: `{error.param.name}`"
    elif isinstance(error, commands.CommandOnCooldown):
        embed.title = "⏳ Cooldown"
        embed.description = f"Try again in **{error.retry_after:.1f}** seconds."
    elif isinstance(error, commands.NotOwner):
        embed.title = "👑 Owner Only"
        embed.description = "This command is restricted to the bot owner."
    else:
        embed.title = "⚠️ Error"
        embed.description = f"An unexpected error occurred."
        print(f"Error in {ctx.command}: {error}")
        traceback.print_exc()

    embed.set_footer(text="Need help? Join our support server!")

    try:
        await ctx.send(embed=embed, delete_after=15)
    except:
        pass

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Global error handler for slash commands"""
    bot.errors_caught += 1

    embed = discord.Embed(color=0xFF4444, title="⚠️ Error")

    if isinstance(error, discord.app_commands.CommandOnCooldown):
        embed.title = "⏳ Cooldown"
        embed.description = f"Try again in **{error.retry_after:.1f}** seconds."
    elif isinstance(error, discord.app_commands.MissingPermissions):
        embed.title = "🔒 Missing Permissions"
        embed.description = "You don't have permission to use this command."
    else:
        embed.description = "An unexpected error occurred."
        print(f"Slash command error: {error}")

    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        pass

# ═══════════════════════════════════════════════════════════════
#  🚀 START BOT
# ═══════════════════════════════════════════════════════════════

# Start web server for Render
keep_alive()

if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        print("\n🔑 Token found, starting bot...")
        bot.run(token, log_handler=None)
    else:
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ❌ ERROR: DISCORD_TOKEN not found!                          ║")
        print("║                                                              ║")
        print("║  Please add your bot token to environment variables:        ║")
        print("║  • Render: Dashboard → Environment → Add DISCORD_TOKEN      ║")
        print("║  • Replit: Secrets tab → Add DISCORD_TOKEN                  ║")
        print("╚══════════════════════════════════════════════════════════════╝")