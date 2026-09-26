import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
class SampleModal(discord.ui.Modal, title="Interactive Feedback Form"):
    """Example Modal Popup with Text Inputs"""
    name_input = discord.ui.TextInput(
        label="Your Name / Handle",
        placeholder="e.g., Alex#1234",
        required=True,
        max_length=50
    )
    feedback_input = discord.ui.TextInput(
        label="Your Feedback / Feature Request",
        style=discord.TextStyle.paragraph,
        placeholder="Type your suggestions here...",
        required=True,
        max_length=1000
    )
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📥 Modal Submission Received!",
            description=f"**From:** {self.name_input.value}\n**Feedback:** {self.feedback_input.value}",
            color=discord.Color.brand_green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
class SampleControlView(discord.ui.View):
    """Example UI View with Interactive Buttons & Dropdown Select Menu"""
    def __init__(self, timeout: float = 180.0):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Accept Rules", style=discord.ButtonStyle.success, emoji="", custom_id="btn_accept")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(" You accepted the server rules!", ephemeral=True)
    @discord.ui.button(label="Open Form", style=discord.ButtonStyle.primary, emoji="📝", custom_id="btn_form")
    async def form_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SampleModal())
    @discord.ui.select(
        placeholder="Choose your primary operating system...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Linux / EterOS", description="Open-source power", emoji="🐧", value="linux"),
            discord.SelectOption(label="Windows", description="Desktop standard", emoji="", value="windows"),
            discord.SelectOption(label="macOS", description="Apple ecosystem", emoji="", value="macos")
        ]
    )
    async def select_os(self, interaction: discord.Interaction, select: discord.ui.Select):
        selected = select.values[0]
        await interaction.response.send_message(f"️ You selected: **{selected.upper()}**", ephemeral=True)
class ExampleCog(commands.Cog, name="Example System"):
    """Comprehensive Cog template illustrating Discord bot features"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.background_counter = 0
        self.heartbeat_task.start()                              
    def cog_unload(self):
        self.heartbeat_task.cancel()                                          
    @tasks.loop(minutes=30)
    async def heartbeat_task(self):
        self.background_counter += 1
        print(f"[Heartbeat] Cog background task executed cycle #{self.background_counter}")
    @heartbeat_task.before_loop
    async def before_heartbeat(self):
        await self.bot.wait_until_ready()
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if "ping bot" in message.content.lower():
            await message.add_reaction("")
    @commands.command(name="example", aliases=["ex", "demo"], help="Shows basic prefixed command with rich embeds.")
    @commands.has_permissions(send_messages=True)
    async def prefix_example(self, ctx: commands.Context, *, extra_text: str = "Default parameter"):
        embed = discord.Embed(
            title=" Prefixed Command Output",
            description=f"Hello {ctx.author.mention}! This command was executed using prefixes.",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Input Parameter", value=f"`{extra_text}`", inline=False)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested in #{ctx.channel.name}", icon_url=self.bot.user.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=True)
    @app_commands.command(name="slash_demo", description="Demonstrates slash commands, autocomplete, and choice parameters.")
    @app_commands.describe(
        category="Choose a command category",
        query="Type to search auto-completed options"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="Moderation Tools", value="mod"),
        app_commands.Choice(name="Utility & Info", value="util"),
        app_commands.Choice(name="Entertainment", value="fun")
    ])
    async def slash_demo(self, interaction: discord.Interaction, category: app_commands.Choice[str], query: str):
        embed = discord.Embed(
            title=" Slash Command Executed",
            description=f"Selected Category: **{category.name}** (`{category.value}`)\nQuery: `{query}`",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, view=SampleControlView())
    @slash_demo.autocomplete('query')
    async def query_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        suggestions = ["apples", "bananas", "cherries", "dragonfruit", "elderberries"]
        return [
            app_commands.Choice(name=item, value=item)
            for item in suggestions if current.lower() in item.lower()
        ][:25]
    @commands.hybrid_command(name="panel", description="Displays an interactive control panel with buttons and menus.")
    async def hybrid_panel(self, ctx: commands.Context):
        embed = discord.Embed(
            title="️ Interactive Server Control Panel",
            description="Use the buttons and select menu below to interact with this panel.",
            color=discord.Color.dark_theme()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/123456789/sample_banner.png")
        await ctx.send(embed=embed, view=SampleControlView())
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(" You lack permissions to run this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"️ An unexpected error occurred: `{error}`", ephemeral=True)
async def setup(bot: commands.Bot):
    """Standard extension setup loader"""
    await bot.add_cog(ExampleCog(bot))
