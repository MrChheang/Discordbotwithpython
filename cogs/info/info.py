import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import platform

from config import Colors, Emojis


class InfoSelect(discord.ui.Select):
    def __init__(self, bot, user):
        self.bot = bot
        self.original_user = user

        options = [
            discord.SelectOption(label="Overview", emoji="🏠", value="overview", default=True),
            discord.SelectOption(label="Stats", emoji="📊", value="stats"),
            discord.SelectOption(label="System", emoji="💻", value="system"),
            discord.SelectOption(label="Links", emoji="🔗", value="links"),
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
        if page == "overview":
            return self.overview()
        elif page == "stats":
            return self.stats()
        elif page == "system":
            return self.system()
        elif page == "links":
            return self.links()
        return self.overview()

    def overview(self):
        # Bot creation timestamp
        created_ts = int(self.bot.user.created_at.timestamp())

        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name="Developer", value="<@1464984679982567454>", inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Created", value=f"<t:{created_ts}:R>", inline=True)

        embed.set_footer(text="Use the menu to explore more")
        embed.timestamp = datetime.now(timezone.utc)
        return embed

    def stats(self):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Statistics", icon_url=self.bot.user.display_avatar.url)

        embed.add_field(name="Servers", value=f"```{len(self.bot.guilds)}```", inline=True)
        embed.add_field(name="Users", value=f"```{len(set(self.bot.get_all_members()))}```", inline=True)
        embed.add_field(name="Ping", value=f"```{round(self.bot.latency * 1000)}ms```", inline=True)

        # Uptime
        delta = datetime.now(timezone.utc) - self.bot.start_time
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)

        embed.add_field(name="Uptime", value=f"```{hours}h {minutes}m {seconds}s```", inline=False)

        embed.timestamp = datetime.now(timezone.utc)
        return embed

    def system(self):
        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="System", icon_url=self.bot.user.display_avatar.url)

        embed.add_field(name="Python", value=f"```{platform.python_version()}```", inline=True)
        embed.add_field(name="discord.py", value=f"```{discord.__version__}```", inline=True)
        embed.add_field(name="Platform", value=f"```{platform.system()}```", inline=True)

        embed.timestamp = datetime.now(timezone.utc)
        return embed

    def links(self):
        invite = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"

        embed = discord.Embed(color=Colors.MAIN)
        embed.set_author(name="Links", icon_url=self.bot.user.display_avatar.url)

        embed.add_field(name="Invite", value=f"[Add to server]({invite})", inline=True)
        embed.add_field(name="Support", value="[Join server](https://discord.gg/NJZvYZP4Cd)", inline=True)

        embed.timestamp = datetime.now(timezone.utc)
        return embed


class InfoView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=60)
        self.add_item(InfoSelect(bot, user))
        self.message = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass
        self.message = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="View bot information")
    async def info_slash(self, interaction: discord.Interaction):
        view = InfoView(self.bot, interaction.user)
        embed = view.children[0].overview()
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @commands.command(name="info", aliases=["about"])
    async def info_prefix(self, ctx):
        view = InfoView(self.bot, ctx.author)
        embed = view.children[0].overview()
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg


async def setup(bot):
    await bot.add_cog(Info(bot))