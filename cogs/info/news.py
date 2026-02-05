import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from config import Colors

NEWS_DATA = [
    {"version": "1.0.0", "date": "2025-02-01", "title": "Bot Launch!", "highlights": ["Premium bot launched", "Added /ping, /uptime, /info", "Custom prefix per server"]}
]

UPCOMING = ["Moderation commands", "Music system", "Economy & leveling"]

class NewsSelect(discord.ui.Select):
    def __init__(self, bot, user):
        self.bot = bot
        self.original_user = user
        options = [
            discord.SelectOption(label="Latest News", emoji="📰", value="latest", default=True),
            discord.SelectOption(label="All Updates", emoji="📋", value="all"),
            discord.SelectOption(label="Coming Soon", emoji="🔮", value="upcoming"),
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
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="News" if page != "upcoming" else "Coming Soon", icon_url=self.bot.user.display_avatar.url)
        
        if page == "latest" and NEWS_DATA:
            news = NEWS_DATA[0]
            embed.title = f"📢 {news['title']}"
            embed.description = f"**Version:** `{news['version']}`\n**Date:** {news['date']}"
            highlights = "\n".join([f"> • {h}" for h in news["highlights"]])
            embed.add_field(name="What's New", value=highlights, inline=False)
        elif page == "all":
            for news in NEWS_DATA[:5]:
                embed.add_field(name=f"v{news['version']} - {news['title']}", value=f"> {news['date']}", inline=False)
        elif page == "upcoming":
            features = "\n".join([f"> 🔹 {f}" for f in UPCOMING])
            embed.add_field(name="In Development", value=features, inline=False)
        
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
            try: await self.message.edit(view=self)
            except: pass

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="news", description="View bot updates")
    async def news_slash(self, interaction: discord.Interaction):
        view = NewsView(self.bot, interaction.user)
        embed = view.children[0].make_embed("latest")
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @commands.command(name="news", aliases=["updates"])
    async def news_prefix(self, ctx):
        view = NewsView(self.bot, ctx.author)
        embed = view.children[0].make_embed("latest")
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

async def setup(bot):
    await bot.add_cog(News(bot))