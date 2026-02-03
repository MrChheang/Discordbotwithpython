import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance
bot = commands.Bot(
    command_prefix='!',  # Change this to your preferred prefix
    intents=intents,
    help_command=None  # Disable default help command (optional)
)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    print(f'  🤖 Bot is online!')
    print(f'  📛 Logged in as: {bot.user.name}')
    print(f'  🆔 Bot ID: {bot.user.id}')
    print(f'  📊 Servers: {len(bot.guilds)}')
    print(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for commands | !help"
        ),
        status=discord.Status.online
    )

# Event: Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help` for available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
    else:
        print(f"Error: {error}")

# Event: Bot joins a new server
@bot.event
async def on_guild_join(guild):
    print(f"✅ Joined new server: {guild.name} (ID: {guild.id})")

# Event: Bot leaves a server
@bot.event
async def on_guild_remove(guild):
    print(f"❌ Left server: {guild.name} (ID: {guild.id})")

# ═══════════════════════════════════════════════════════════════
# ADD YOUR COMMANDS BELOW THIS LINE
# ═══════════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════════
# END OF COMMANDS SECTION
# ═══════════════════════════════════════════════════════════════

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