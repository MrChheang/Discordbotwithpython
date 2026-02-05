import discord
from discord.ext import commands
import os
import json
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
    'default_prefix': '!',
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


# Load prefixes from file
def load_prefixes():
    try:
        with open('data/prefixes.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Get prefix for a guild
def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(BOT_CONFIG['default_prefix'])(bot, message)
    
    prefixes = load_prefixes()
    prefix = prefixes.get(str(message.guild.id), BOT_CONFIG['default_prefix'])
    return commands.when_mentioned_or(prefix)(bot, message)


class PremiumBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        # Store start time with timezone for uptime tracking
        self.start_time = datetime.now(timezone.utc)
        self.default_prefix = BOT_CONFIG['default_prefix']
        self.developer = BOT_CONFIG['developer']
        self.version = BOT_CONFIG['version']
        self.default_color = BOT_CONFIG['color']
        self.support_server = BOT_CONFIG['support_server']
        self.github = BOT_CONFIG['github']
        
        # Debug: Print start time to verify it's set correctly
        print(f"Bot start_time set to: {self.start_time} (timestamp: {int(self.start_time.timestamp())})")

    async def setup_hook(self):
        # Create data folder if not exists
        os.makedirs('data', exist_ok=True)
        
        print()
        print("╔════════════════════════════════════════════════════════════╗")
        print("║              🚀 PREMIUM BOT - LOADING                      ║")
        print("╠════════════════════════════════════════════════════════════╣")
        
        cogs = [
            'cogs.info.ping',
            'cogs.info.uptime',
            'cogs.info.info',
            'cogs.setup.prefix',
            'cogs.developer.dev'
        ]
        
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


class MentionSelect(discord.ui.Select):
    def __init__(self, bot, user):
        self.bot = bot
        self.original_user = user
        
        options = [
            discord.SelectOption(label="Bot Information", emoji="🤖", value="info", description="Learn about the bot"),
            discord.SelectOption(label="Changelogs", emoji="📋", value="changelog", description="Recent updates"),
            discord.SelectOption(label="Support", emoji="💬", value="support", description="Get help"),
        ]
        
        super().__init__(placeholder="What would you like to know?", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.original_user.id:
            return await interaction.response.send_message("This menu isn't for you.", ephemeral=True)
        
        if self.values[0] == "info":
            embed = self.bot_info()
        elif self.values[0] == "changelog":
            embed = self.changelog()
        elif self.values[0] == "support":
            embed = self.support()
        
        for opt in self.options:
            opt.default = opt.value == self.values[0]
        
        await interaction.response.edit_message(embed=embed, view=self.view)
    
    def bot_info(self):
        embed = discord.Embed(color=0x5DBB63)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.description = f"A premium Discord bot designed to enhance your server experience with powerful features and reliable performance."
        
        embed.add_field(name="Developer", value="<@1464984679982567454>", inline=True)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="Users", value=f"`{len(set(self.bot.get_all_members()))}`", inline=True)
        
        embed.add_field(name="Prefix", value="`!` or `/`", inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Version", value=f"`{self.bot.version}`", inline=True)
        
        return embed
    
    def changelog(self):
        embed = discord.Embed(color=0x5DBB63)
        embed.set_author(name="Changelogs", icon_url=self.bot.user.display_avatar.url)
        
        embed.description = "Latest updates and improvements"
        
        embed.add_field(
            name="📦 v1.0.0 - Initial Release",
            value="> • Premium bot launched\n> • Added /ping, /uptime, /info commands\n> • Custom prefix per server\n> • Auto-updating status",
            inline=False
        )
        
        embed.add_field(
            name="🔮 Coming Soon",
            value="> • Moderation commands\n> • Music features\n> • Economy system\n> • Leveling system",
            inline=False
        )
        
        embed.set_footer(text="Stay tuned for more updates!")
        
        return embed
    
    def support(self):
        embed = discord.Embed(color=0x5DBB63)
        embed.set_author(name="Support", icon_url=self.bot.user.display_avatar.url)
        
        embed.description = "Need help? We're here for you!"
        
        embed.add_field(
            name="💬 Support Server",
            value=f"[Click to join](https://discord.gg/NJZvYZP4Cd)",
            inline=False
        )
        
        embed.add_field(
            name="📌 Quick Help",
            value="> • Use `/help` to see all commands\n> • Use `/info` for bot information\n> • Server owner can use `/setup-prefix` to change prefix",
            inline=False
        )
        
        embed.add_field(
            name="🐛 Found a Bug?",
            value="Report it in our support server and we'll fix it ASAP!",
            inline=False
        )
        
        embed.set_footer(text="Thanks for using our bot! 💚")
        
        return embed


class MentionView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=120)
        self.add_item(MentionSelect(bot, user))
        self.message = None
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Check if bot is mentioned
    if bot.user in message.mentions:
        embed = discord.Embed(color=0x5DBB63)
        embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        
        embed.description = f"Hey {message.author.mention}! 👋\n\nThanks for reaching out! I'm a premium bot here to help your server.\n\nUse the menu below to learn more about me."
        
        embed.add_field(
            name="Quick Start",
            value=f"> **Prefix:** `!` or `/`\n> **Help:** `/help` or `!help`\n> **Info:** `/info` or `!info`",
            inline=False
        )
        
        embed.set_footer(text="Select an option below to continue")
        
        view = MentionView(bot, message.author)
        msg = await message.channel.send(embed=embed, view=view)
        view.message = msg
    
    await bot.process_commands(message)


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