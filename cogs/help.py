import discord
from discord.ext import commands
class HelpView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed], author_id: int, timeout: float = 120.0):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.author_id = author_id
        self.current_page = 0
        self.update_buttons()
    def update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == len(self.pages) - 1)
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(" This menu belongs to someone else!", ephemeral=True)
            return False
        return True
    @discord.ui.button(label="Prev.", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)
class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the bot connection latency."""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title=" Pong!",
            description=f"Bot Latency: **{latency}ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    @commands.command(name="help")
    async def help_command(self, ctx):
        """Interactive help menu organized by category."""
        pages = []
        for cog_name, cog in self.bot.cogs.items():
            cmds = cog.get_commands()
            visible_cmds = [cmd for cmd in cmds if not cmd.hidden]
            if not visible_cmds:
                continue
            category_title = cog_name.replace("Cog", "").upper()
            embed = discord.Embed(
                title=f"📖 Command Category: {category_title}",
                description="Use the buttons below to switch categories.",
                color=discord.Color.blue()
            )
            for cmd in visible_cmds:
                desc = cmd.help or "No description provided."
                embed.add_field(
                    name=f"**c!{cmd.name}**",
                    value=f"└ {desc}",
                    inline=False
                )
            pages.append(embed)
        uncategorized = [cmd for cmd in self.bot.commands if cmd.cog is None and not cmd.hidden]
        if uncategorized:
            embed = discord.Embed(
                title="📖 Command Category: GENERAL",
                description="Use the buttons below to switch categories.",
                color=discord.Color.blue()
            )
            for cmd in uncategorized:
                desc = cmd.help or "No description provided."
                embed.add_field(
                    name=f"**c!{cmd.name}**",
                    value=f"└ {desc}",
                    inline=False
                )
            pages.append(embed)
        if not pages:
            return await ctx.send(" No commands available.")
        total_pages = len(pages)
        for idx, page in enumerate(pages):
            page.set_footer(text=f"Page {idx + 1} of {total_pages} • Prefix: c!")
        view = HelpView(pages=pages, author_id=ctx.author.id)
        if total_pages == 1:
            view.children[0].disabled = True
            view.children[1].disabled = True
        await ctx.send(embed=pages[0], view=view)
async def setup(bot):
    await bot.add_cog(HelpCog(bot))
