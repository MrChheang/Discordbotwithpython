import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timezone
import traceback
import logging
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO, format='%(asctime)s │ %(levelname)-8s │ %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

BOT_CONFIG = {
    'default_prefix': '!',
    'developer': '<@1464984679982567454>',
    'version': '1.0.0',
    'color': 0x5865F2,
    'support_server': 'https://discord.gg/NJZvYZP4Cd',
    'github': None
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

def load_prefixes():
    try:
        with open('data/prefixes.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(BOT_CONFIG['default_prefix'])(bot, message)
    prefixes = load_prefixes()
    prefix = prefixes.get(str(message.guild.id), BOT_CONFIG['default_prefix'])
    return commands.when_mentioned_or(prefix)(bot, message)

class PremiumBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None, case_insensitive=True)
        self.start_time = datetime.now(timezone.utc)
        self.default_prefix = BOT_CONFIG['default_prefix']
        self.developer = BOT_CONFIG['developer']
        self.version = BOT_CONFIG['version']
        self.default_color = BOT_CONFIG['color']
        self.support_server = BOT_CONFIG['support_server']
        self.github = BOT_CONFIG['github']

    async def setup_hook(self):
        os.makedirs('data', exist_ok=True)
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║              🚀 PREMIUM BOT - LOADING                      ║")
        print("╠════════════════════════════════════════════════════════════╣")
        
        cogs = ['cogs.info.ping', 'cogs.info.uptime', 'cogs.info.info', 'cogs.info.news', 'cogs.setup.prefix', 'cogs.mod.mod', 'cogs.developer.dev']
        
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
    print(f"\n🌟 {bot.user.name} is online! | {len(bot.guilds)} servers")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | {len(bot.guilds)} servers"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot.user in message.mentions:
        embed = discord.Embed(color=0x5DBB63, description=f"Hey {message.author.mention}! 👋\n\nMy prefix is `!` or use `/` for slash commands.")
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

keep_alive()

if __name__ == "__main__":
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        print("\n🔑 Starting bot...")
        bot.run(token, log_handler=None)
    else:
        print("\n❌ DISCORD_TOKEN not found!")