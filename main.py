import discord
from discord.ext import commands
import os
import asyncio
from datetime import datetime
from keep_alive import keep_alive

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance with both prefix and slash command support
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',  # Change this to your preferred prefix
            intents=intents,
            help_command=None  # Disable default help command
        )
        self.start_time = datetime.utcnow()  # Track bot start time for uptime
        self.developer = "YourName"  # Change to your name/username

    async def setup_hook(self):
        # Load all cogs
        cog_files = [
            'cogs.info.ping',
            'cogs.info.uptime',
            'cogs.info.info'
        ]

        for cog in cog_files:
            try:
                await self.load_extension(cog)
                print(f'✅ Loaded: {cog}')
            except Exception as e:
                print(f'❌ Failed to load {cog}: {e}')

        # Sync slash commands globally
        try:
            synced = await self.tree.sync()
            print(f'🔄 Synced {len(synced)} slash command(s)')
        except Exception as e:
            print(f'❌ Failed to sync commands: {e}')

bot = MyBot()

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print(f'  🤖 Bot is online!')
    print(f'  📛 Logged in as: {bot.user.name}')
    print(f'  🆔 Bot ID: {bot.user.id}')
    print(f'  📊 Servers: {len(bot.guilds)}')
    print(f'  👥 Users: {len(set(bot.get_all_members()))}')
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/help | !help"
        ),
        status=discord.Status.online
    )

# Event: Error handling for prefix commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help` or `/help` for available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Command on cooldown. Try again in {error.retry_after:.1f}s")
    else:
        print(f"Error: {error}")

# Start the web server for Render
keep_alive()

# Run the bot
if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: DISCORD_TOKEN environment variable not set!")
        print("Please add your bot token to the environment variables.")