import discord
from discord.ext import commands
import os
from datetime import datetime, timezone
import traceback
import logging
from keep_alive import keep_alive

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Bot config
BOT_CONFIG = {
    'prefix': '!',
    'developer': '<@1464984679982567454>',
    'version': '1.0.0',
    'color': 0x5865F2,
    'support_server': 'https://discord.gg/NJZvYZP4Cd',
    'github': None
}

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True


class PremiumBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(BOT_CONFIG['prefix']),
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        # Store start time with timezone for uptime tracking
        self.start_time = datetime.now(timezone.utc)
        self.developer = BOT_CONFIG['developer']
        self.version = BOT_CONFIG['version']
        self.default_color = BOT_CONFIG['color']
        self.support_server = BOT_CONFIG['support_server']
        self.github = BOT_CONFIG['github']

        # Debug: Print start time to verify it's set correctly
        print(f"Bot start_time set to: {self.start_time} (timestamp: {int(self.start_time.timestamp())})")

    async def setup_hook(self):
        print()
        print("╔════════════════════════════════════════════════════════════╗")
        print("║              🚀 PREMIUM BOT - LOADING                      ║")
        print("╠════════════════════════════════════════════════════════════╣")

        cogs = ['cogs.info.ping', 'cogs.info.uptime', 'cogs.info.info']

        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"║  ✅ Loaded: {cog:<46} ║")
            except Exception as e:
                print(f"║  ❌ Failed: {cog:<46} ║")
                traceback.print_exc()

        print("╚════════════════════════════════════════════════════════════╝")

        try:
            synced = await self.tree.sync()
            print(f"\n🔄 Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"\n❌ Sync failed: {e}")


bot = PremiumBot()


@bot.event
async def on_ready():
    print()
    print(f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"┃                    🌟 BOT IS ONLINE 🌟                      ┃")
    print(f"┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    print(f"┃  🤖 {bot.user.name:<54} ┃")
    print(f"┃  📊 {len(bot.guilds)} servers | {len(set(bot.get_all_members()))} users                              ┃")
    print(f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"/help | {len(bot.guilds)} servers"
        )
    )


@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(color=0xFF4444, title="❌ Error")

    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed.description = "You don't have permission."
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.description = f"Missing argument: `{error.param.name}`"
    else:
        embed.description = "Something went wrong."
        print(f"Error: {error}")

    await ctx.send(embed=embed, delete_after=10)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    embed = discord.Embed(color=0xFF4444, title="❌ Error", description="Something went wrong.")

    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        pass


keep_alive()

if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        print("\n🔑 Starting bot...")
        bot.run(token, log_handler=None)
    else:
        print("\n❌ DISCORD_TOKEN not found!")