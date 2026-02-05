import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone

from config import Colors, Emojis


# ═══════════════════════════════════════════════════════════════
#  NEWS DATA - Edit this to update news
# ═══════════════════════════════════════════════════════════════

NEWS_DATA = [
    {
        "version": "1.1.0",
        "date": "2025-02-05",
        "title": "News System Added",
        "type": "feature",  # feature, update, fix, announcement
        "highlights": [
            "Added /news command to view updates",
            "New select menu for browsing news",
            "Beautiful embed design"
        ]
    },
    {
        "version": "1.0.0",
        "date": "2025-02-01",
        "title": "Bot Launch! 🚀",
        "type": "announcement",
        "highlights": [
            "Premium bot officially launched",
            "Added /ping, /uptime, /info commands",
            "Custom prefix per server",
            "Developer commands for bot management"
        ]
    }
]

UPCOMING_FEATURES = [
    "Moderation commands (ban, kick, mute)",
    "Music system with queue",
    "Economy & leveling system",
    "Auto-moderation features",
    "Custom welcome messages"
]


class NewsSelect(discord.ui.Select):
    def __init__(self, bot, user):
        self.bot = bot
        self.original_user = user
        
        options = [
            discord.SelectOption(label="Latest News", emoji="📰", value="latest", default=True, description="Most recent update"),
            discord.SelectOption(label="All Updates", emoji="📋", value="all", description="View all past updates"),
            discord.SelectOption(label="Coming Soon", emoji="🔮", value="upcoming", description="Features in development"),
        ]
        
        super().__init__(placeholder="Select a category", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.original_user.id:
            return await interaction.response.send_message("This isn't your menu.", ephemeral=True)
        
        for opt in self.options:
            opt.default = opt.value == self.values[0]
        
        embed = self.make_embed(self.values[0])
        await interaction.response.edit_message(embed=embed, view=self.view)
    
    def make_embed(self, page):
        if page == "latest":
            return self.latest_news()
        elif page == "all":
            return self.all_updates()
        elif page == "upcoming":
            return self.upcoming()
        return self.latest_news()
    
    def get_type_emoji(self, news_type):
        types = {
            "feature": "✨",
            "update": "📦",
            "fix": "🔧",
            "announcement": "📢"
        }
        return types.get(news_type, "📰")
    
    def latest_news(self):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Latest News", icon_url=self.bot.user.display_avatar.url)
        
        if NEWS_DATA:
            news = NEWS_DATA[0]
            type_emoji = self.get_type_emoji(news["type"])
            
            embed.title = f"{type_emoji} {news['title']}"
            embed.description = f"**Version:** `{news['version']}`\n**Date:** {news['date']}"
            
            highlights = "\n".join([f"> • {h}" for h in news["highlights"]])
            embed.add_field(name="What's New", value=highlights, inline=False)
        else:
            embed.description = "No news available yet."
        
        embed.set_footer(text="Use the menu to see more")
        embed.timestamp = datetime.now(timezone.utc)
        return embed
    
    def all_updates(self):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="All Updates", icon_url=self.bot.user.display_avatar.url)
        embed.description = "Complete update history"
        
        for news in NEWS_DATA[:5]:  # Show last 5 updates
            type_emoji = self.get_type_emoji(news["type"])
            highlights = " • ".join(news["highlights"][:2])
            if len(news["highlights"]) > 2:
                highlights += " ..."
            
            embed.add_field(
                name=f"{type_emoji} v{news['version']} - {news['title']}",
                value=f"> {news['date']}\n> {highlights}",
                inline=False
            )
        
        embed.set_footer(text=f"Showing {min(5, len(NEWS_DATA))} of {len(NEWS_DATA)} updates")
        embed.timestamp = datetime.now(timezone.utc)
        return embed
    
    def upcoming(self):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Coming Soon", icon_url=self.bot.user.display_avatar.url)
        embed.description = "Features we're working on"
        
        features = "\n".join([f"> 🔹 {f}" for f in UPCOMING_FEATURES])
        embed.add_field(name="In Development", value=features, inline=False)
        
        embed.add_field(
            name="💡 Have a suggestion?",
            value=f"Join our [support server](https://discord.gg/NJZvYZP4Cd) to suggest features!",
            inline=False
        )
        
        embed.set_footer(text="Stay tuned for updates!")
        embed.timestamp = datetime.now(timezone.utc)
        return embed


class NewsView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=60)
        self.add_item(NewsSelect(bot, user))
        self.message = None
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="news", description="View bot updates and announcements")
    async def news_slash(self, interaction: discord.Interaction):
        view = NewsView(self.bot, interaction.user)
        embed = view.children[0].latest_news()
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @commands.command(name="news", aliases=["updates", "changelog"])
    async def news_prefix(self, ctx):
        view = NewsView(self.bot, ctx.author)
        embed = view.children[0].latest_news()
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg


async def setup(bot):
    await bot.add_cog(News(bot))